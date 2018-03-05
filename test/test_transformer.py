import glob
import logging
from pathlib import Path
import unittest
from unittest import TestCase

from lark import Tree
from lark.common import UnexpectedToken

from quippy.parser import quipper_parser
from quippy.transformer import *

logger = logging.getLogger(__name__)


class TestTransformer(TestCase):
    def parser(self, start='start'):
        return quipper_parser(start=start, transformer=QuipperTransformer())

    def test_arity(self):
        basic_text = """0:Qbit
        """
        parser = self.parser(start='arity')
        parsed = parser.parse(basic_text)
        self.assertEqual([TypeAssignment(wire=0, type=TypeAssignment.Type.Qbit)], parsed)

    def test_circuit(self):
        basic_text = """Inputs: 0:Qbit, 1:Cbit
        Outputs: 0:Qbit, 1:Cbit
        """
        parser = self.parser(start='circuit')
        parsed = parser.parse(basic_text)
        self.assertEqual(Circuit(
            inputs=[TypeAssignment(0, TypeAssignment.Type.Qbit),
                    TypeAssignment(1, TypeAssignment.Type.Cbit)],
            gates=[],
            outputs=[TypeAssignment(0, TypeAssignment.Type.Qbit),
                     TypeAssignment(1, TypeAssignment.Type.Cbit)],
            ), parsed)

    def test_qgate(self):
        text = '''QGate["not"](0) with controls=[+2,-3] with nocontrol'''
        parser = self.parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(QGate(
            name="not",
            inverted=False,
            wire=0,
            control=Control(controlled=[2, -3], no_control=True)
            ), parsed)

    def test_statement_comment(self):
        basic_text = '''Comment["ENTER: qft_big_endian"](0:"qs[0]", 1:"qs[1]")'''
        parser = self.parser(start='gate')
        parsed = parser.parse(basic_text)
        self.assertEqual(Comment(
            comment="ENTER: qft_big_endian",
            wire_comments=[
                (Wire(i=0), "qs[0]"),
                (Wire(i=1), "qs[1]")
                ]
            ), parsed)

    def test_qinit_gate(self):
        text = '''QInit1(0) with nocontrol'''
        parser = self.parser('gate')
        parsed = parser.parse(text)
        self.assertEqual(QInit(value=True, wire=Wire(i=0)), parsed)

    def test_sub_call_x1(self):
        text = '''Subroutine["SP", shape "([Q,Q,Q],())"] (3,4,5) -> (0,1,2) with controls=[+5] with nocontrol'''
        parser = self.parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(SubroutineCall(
            repetitions=1,
            name="SP",
            shape="([Q,Q,Q],())",
            inverted=False,
            inputs=[Wire(3), Wire(4), Wire(5)],
            outputs=[Wire(0), Wire(1), Wire(2)],
            control=Control(controlled=[Wire(5)], no_control=True)
            ), parsed)

    def test_sub_call_x154(self):
        text = '''Subroutine(x154)["SP", shape "([Q,Q,Q],())"] (3,4,5) -> (0,1,2)'''
        parser = self.parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(SubroutineCall(
            repetitions=154,
            name="SP",
            shape="([Q,Q,Q],())",
            inverted=False,
            inputs=[Wire(3), Wire(4), Wire(5)],
            outputs=[Wire(0), Wire(1), Wire(2)],
            control=Control(controlled=[], no_control=False)
            ), parsed)

    def test_subroutine(self):
        text = '''
        Subroutine: "S1"
        Shape: "([Q],())"
        Controllable: yes
        Inputs: 0:Qbit
        QGate["H"]*(0) with controls=[+3,-5, -6] with nocontrol
        QRot["bla", 1e-05](1)
        Outputs: 0:Qbit
        '''
        parser = self.parser(start='subroutine')
        parsed: Subroutine = parser.parse(text)
        # Break the equality check into two steps because it is too big.
        circuit = parsed.circuit
        expected_circuit = Circuit(
            inputs=[TypeAssignment(Wire(0), TypeAssignment.Type.Qbit)],
            gates=[
                QGate(
                    name="H",
                    inverted=True,
                    wire=Wire(0),
                    control=Control(
                        controlled=[
                            Wire(3),
                            Wire(-5),
                            Wire(-6)
                            ],
                        no_control=True
                        )
                    ),
                QRot(
                    name="bla",
                    timestep=1e-05,
                    wire=Wire(1)
                    )
                ],
            outputs=[TypeAssignment(Wire(0), TypeAssignment.Type.Qbit)]
            )
        self.assertEqual(expected_circuit, circuit)
        self.assertEqual(Subroutine(
            name="S1",
            shape="([Q],())",
            controllable=Subroutine.Control.yes,
            circuit=expected_circuit
            ), parsed)

    @unittest.skip
    def test_optimizer(self):
        """Try to parse all files in the optimizer resource folder."""
        optimizer_files_path = Path(__file__).parents[1] / "resources" / "optimizer" / "**"
        optimizer_files = glob.glob(str(optimizer_files_path), recursive=True)
        quipper_paths = filter(lambda path: not path.is_dir()
                                            and path.suffix == '',
                               map(lambda s: Path(s), optimizer_files))
        parser = quipper_parser()
        for path in quipper_paths:
            print(path)
            with open(path) as quipper_file:
                try:
                    self.parser().parse(quipper_file.read())
                except UnexpectedToken as e:
                    raise RuntimeError(f"Failed to parse {path}. Error: {e}")

    @unittest.skip
    def test_simcount(self):
        """Try to parse all files in the simcount resource folder."""
        simcount_files_path = Path("resources") / "simcount"
        if (not simcount_files_path.exists()):
            logger.warning('''simcount resource does not exist, skipping tests!
            Download the resource from https://github.com/njross/simcount/blob/master/samples.tar.gz
            and put the extracted folder in resources named "simcount".
            ''')
            return

        simcount_files = glob.glob(str(simcount_files_path / "**"), recursive=True)
        quipper_paths = filter(lambda path: not path.is_dir()
                                            and path.suffix == '',
                               map(lambda s: Path(s), simcount_files))
        parser = quipper_parser()
        for path in quipper_paths:
            print(path)
            with open(path) as quipper_file:
                try:
                    self.parser().parse(quipper_file.read())
                except UnexpectedToken as e:
                    raise RuntimeError(f"Failed to parse {path}. Error: {e}")
