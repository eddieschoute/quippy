import glob
from pathlib import Path
from unittest import TestCase

from tatsu.exceptions import FailedParse

import _model
import _parser


class TestModel(TestCase):
    def setUp(self):
        self.parser = _parser.QuipperParser(semantics=_model.QuipperModelBuilderSemantics())

    def test_typeassignment(self):
        basic_text = """0:Qbit"""
        parsed: _model.TypeAssignment = self.parser.parse(basic_text, rule_name="type_assignment")
        self.assertEqual(0, parsed.number)
        self.assertEqual("Qbit", parsed.type)

    def test_start(self):
        basic_text = """Inputs: 0:Qbit, 1:Qbit
        Outputs: 0:Qbit, 1:Qbit
        """
        parsed: _model.Circuit = self.parser.parse(basic_text, rule_name="circuit")
        self.assertEqual(2, len(parsed.inputs))
        self.assertEqual(0, len(parsed.gatelist))
        self.assertEqual(2, len(parsed.outputs))
        self.assertEqual(0, parsed.inputs[0].number)
        self.assertEqual('Qbit', parsed.inputs[0].type)
        self.assertEqual(1, parsed.inputs[1].number)

    def test_gatelist_qgate(self):
        basic_text = '''QGate["not"](0) with controls=[+2,-3] with nocontrol'''
        parsed: _model.QGate = self.parser.parse(basic_text, rule_name="gate")
        self.assertEqual('not', parsed.name)
        self.assertEqual(None, parsed.inverse)
        self.assertEqual(2, len(parsed.controlled.controls))
        self.assertEqual(2, parsed.controlled.controls[0])
        self.assertEqual(-3, parsed.controlled.controls[1])

    def test_wire(self):
        basic_text = '''0:"qs[0]"'''
        parsed: _model.Wire = self.parser.parse(basic_text, rule_name="wire")
        self.assertEqual('qs[0]', parsed.text)
        self.assertEqual(0, parsed.qubit)

    def test_statement_comment(self):
        basic_text = '''Comment["ENTER: qft_big_endian"](0:"qs[0]", 1:"qs[1]")'''
        parsed: _model.Comment = self.parser.parse(basic_text, rule_name="comment")
        self.assertEqual('ENTER: qft_big_endian', parsed.text)
        self.assertEqual(2, len(parsed.wires))
        self.assertEqual(0, parsed.wires[0].qubit)
        self.assertEqual('qs[1]', parsed.wires[1].text)

    def test_subroutine(self):
        text = '''
        Subroutine: "L"
        Shape: "([Q,Q],())"
        Controllable: yes
        Inputs: 0:Qbit, 1:Qbit
        QGate["H"](0) with nocontrol
        QGate["H"](1) with nocontrol
        Outputs: 0:Qbit, 1:Qbit
        '''
        parsed: _model.Subroutine = self.parser.parse(text, rule_name="subroutine")
        self.assertEqual("L", parsed.name)
        self.assertEqual("([Q,Q],())", parsed.shape)
        self.assertEqual("yes", parsed.controllable)
        self.assertEqual(2, len(parsed.circuit.gatelist))

    def test_circuit_subroutine(self):
        text = '''Inputs: 0:Qbit, 1:Qbit
        Subroutine(x1)["L", shape "([Q,Q))"] (0,1) -> (0,1)
        Subroutine(x26445964)["C", shape "([Q,Q))"] (0,1) -> (0,1)
        Subroutine(x1)["R", shape "([Q,Q))"] (0,1) -> (0,1)
        Outputs: 0:Qbit, 1:Qbit
        
        Subroutine: "L"
        Shape: "([Q,Q],())"
        Controllable: yes
        Inputs: 0:Qbit, 1:Qbit
        QGate["H"](0) with nocontrol
        QGate["H"](1) with nocontrol
        Outputs: 0:Qbit, 1:Qbit
        '''
        parsed: _model.BCircuit = self.parser.parse(text)
        self.assertEqual(1, len(parsed.subroutines))
        self.assertEqual("L", parsed.subroutines[0].name)
        self.assertEqual(1, parsed.subroutines[0].circuit.outputs[1].number)

    def test_real(self):
        """Try to parse all files in the optimizer resource folder."""
        optimizer_files_path = Path("resources") / "optimizer" / "**"
        optimizer_files = glob.glob(str(optimizer_files_path), recursive=True)
        quipper_paths = filter(lambda path: not path.is_dir()
                                            and path.suffix == '',
                               map(lambda s: Path(s), optimizer_files))
        for path in quipper_paths:
            print(path)
            with open(path) as quipper_file:
                try:
                    self.parser.parse(quipper_file.read())
                except FailedParse as e:
                    raise RuntimeError(f"Failed to parse {path}. Error: {e}")
