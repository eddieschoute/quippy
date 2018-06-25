# Copyright 2018 Eddie Schoute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import glob
import logging
from pathlib import Path
import unittest
from unittest import TestCase

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
        self.assertEqual([TypeAssignment(wire=Wire(0), type=TypeAssignment_Type.Qbit)], parsed)

    def test_circuit(self):
        basic_text = """Inputs: 0:Qbit, 1:Cbit
        Outputs: 0:Qbit, 1:Cbit
        """
        parser = self.parser(start='circuit')
        parsed = parser.parse(basic_text)
        self.assertEqual(Circuit(
            inputs=[TypeAssignment(Wire(0), TypeAssignment_Type.Qbit),
                    TypeAssignment(Wire(1), TypeAssignment_Type.Cbit)],
            gates=[],
            outputs=[TypeAssignment(Wire(0), TypeAssignment_Type.Qbit),
                     TypeAssignment(Wire(1), TypeAssignment_Type.Cbit)],
            ), parsed)

    def test_qgate(self):
        text = '''QGate["not"](0) with controls=[+2,-3] with nocontrol'''
        parser = self.parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(QGate(
            op=QGate_Op.Not,
            inverted=False,
            wire=Wire(0),
            control=Control(controlled=[Wire(2), Wire(-3)], no_control=True)
            ), parsed)

    def test_statement_comment(self):
        basic_text = '''Comment["ENTER: qft_big_endian"](0:"qs[0]", 1:"qs[1]")'''
        parser = self.parser(start='gate')
        parsed = parser.parse(basic_text)
        self.assertEqual(Comment(
            comment="ENTER: qft_big_endian",
            inverted=False,
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
        QRot["exp(-i%Z)", 1e-05](1)
        Outputs: 0:Qbit
        '''
        parser = self.parser(start='subroutine')
        parsed = parser.parse(text)  # type: Subroutine
        # Break the equality check into two steps because it is too big.
        circuit = parsed.circuit
        expected_circuit = Circuit(
            inputs=[TypeAssignment(Wire(0), TypeAssignment_Type.Qbit)],
            gates=[
                QGate(
                    op=QGate_Op.H,
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
                    op=QRot_Op.ExpZt,
                    timestep=1e-05,
                    inverted=False,
                    wire=Wire(1)
                    )
                ],
            outputs=[TypeAssignment(Wire(0), TypeAssignment_Type.Qbit)]
            )
        self.assertEqual(expected_circuit, circuit)
        self.assertEqual(Subroutine(
            name="S1",
            shape="([Q],())",
            controllable=Subroutine_Control.yes,
            circuit=expected_circuit
            ), parsed)

    def test_start(self):
        text = '''Inputs: 0:Qbit
        QGate["H"]*(0) with controls=[+3,-5, -6] with nocontrol
        QRot["exp(-i%Z)", 1e-05](1)
        Outputs: 0:Qbit
        '''
        parser = self.parser()
        parsed = parser.parse(text)  # type: Subroutine
        expected_start = Start(
            circuit=Circuit(
                inputs=[TypeAssignment(Wire(0), TypeAssignment_Type.Qbit)],
                gates=[
                    QGate(
                        op=QGate_Op.H,
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
                        op=QRot_Op.ExpZt,
                        timestep=1e-05,
                        inverted=False,
                        wire=Wire(1)
                        )
                    ],
                outputs=[TypeAssignment(Wire(0), TypeAssignment_Type.Qbit)]
                ),
            subroutines=[]
            )
        self.assertEqual(expected_start, parsed)

    def test_optimizer_pf6_30_before(self):
        """Try to parse all files in the optimizer resource folder."""
        pf6_30_before = Path(__file__).parents[1] / "resources" / "optimizer" / "PF" / "pf6_30_before"
        parser = self.parser()
        with open(str(pf6_30_before)) as quipper_file:
            try:
                parser.parse(quipper_file.read())
            except:
                e = sys.exc_info()[0]
                raise RuntimeError(f"Failed to parse {path}. Error: {e.message}")

    def test_optimizer_pf6_100_before(self):
        """Try to parse pf6_100 in the optimizer resource folder."""
        pf6_100_before = Path(__file__).parents[1] / "resources" / "optimizer" / "PF" / "pf6_100_before"
        parser = self.parser()
        with open(str(pf6_100_before), 'r') as quipper_file:
            try:
                parser.parse(quipper_file.read())
            except:
                e = sys.exc_info()[0]
                raise RuntimeError(f"Failed to parse {path}. Error: {e.message}")

    @unittest.skip("Long test")
    def test_optimizer(self):
        """Try to parse all files in the optimizer resource folder."""
        optimizer_files_path = Path(__file__).parents[1] / "resources" / "optimizer" / "**"
        optimizer_files = glob.glob(str(optimizer_files_path), recursive=True)
        quipper_paths = filter(lambda path: not path.is_dir()
                                            and path.suffix == '',
                               map(lambda s: Path(s), optimizer_files))
        parser = self.parser()
        for path in quipper_paths:
            print(path)
            with open(str(path)) as quipper_file:
                try:
                    parser.parse(quipper_file.read())
                except:
                    e = sys.exc_info()[0]
                    raise RuntimeError(f"Failed to parse {path}. Error: {e.message}")

    @unittest.skip("Long test")
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
        parser = self.parser()
        success = True
        for path in quipper_paths:
            print(path)
            with open(str(path)) as quipper_file:
                try:
                    parser.parse(quipper_file.read())
                except:
                    e = sys.exc_info()[0]
                    print(f"Failed to parse {path}. Error: {e.message}")
                    success = False
        self.fail()
