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
        self.assertEqual(2, len(parsed.input.qubits))
        self.assertEqual(0, len(parsed.gatelist))
        self.assertEqual(2, len(parsed.output.qubits))
        self.assertEqual(0, parsed.input.qubits[0])
        self.assertEqual(1, parsed.input.qubits[1])

    def test_gatelist_qgate(self):
        basic_text = '''QGate["not"](0) with controls=[+2] with nocontrol'''
        parsed: _model.QGate = self.parser.parse(basic_text, rule_name="gatelist")
        self.assertEqual('not', parsed.name)
        self.assertEqual(None, parsed.inverse)
        self.assertEqual(2, parsed.controlled.control.qubit)

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
