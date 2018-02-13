from unittest import TestCase
from pathlib import Path

import grammar

ADDER_FILE = Path("resources") / "optimizer" / "Arithmetic_and_Toffoli" / "adder_8_before"

class TestGrammar(TestCase):
    def test_iostatement(self):
        basic_text = """Inputs: 0:Qbit"""
        parsed = grammar.quipper_model.parse(basic_text, start="iostatement")
        self.assertEqual(['Inputs', ':', ['0', ':', 'Qbit'], []], parsed)

    def test_start(self):
        basic_text = """Inputs: 0:Qbit, 1:Qbit
        Outputs: 0:Qbit, 1:Qbit"""
        parsed = grammar.quipper_model.parse(basic_text, start="start", asmodel=True)
        self.assertEqual(['Inputs', ':', ['0', ':', 'Qbit'], []], parsed)
