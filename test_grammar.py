from unittest import TestCase
from pathlib import Path

import parser
import tatsu

ADDER_FILE = Path("resources") / "optimizer" / "Arithmetic_and_Toffoli" / "adder_8_before"

class TestGrammar(TestCase):
    def test_iostatement(self):
        basic_text = """Inputs: 0:Qbit"""
        parsed = parser.quipper_model.parse(basic_text, start="iostatement")
        self.assertEqual(['Inputs', ':', ['0', ':', 'Qbit'], []], parsed)

    def test_start(self):
        basic_text = """Inputs: 0:Qbit, 1:Qbit
        Outputs: 0:Qbit, 1:Qbit"""
        parsed = parser.quipper_model.parse(basic_text, start="start", asmodel=True)
        self.assertEqual(['Inputs', ':', ['0', ':', 'Qbit'], []], parsed)

    def test_statement_qgate(self):
        basic_text = '''QGate["not"](0) with controls=[+2] with nocontrol'''
        parsed = parser.quipper_model.parse(basic_text, start="statement", asmodel=True)
        self.assertEqual(['Inputs', ':', ['0', ':', 'Qbit'], []], parsed)

    def test_statement_comment(self):
        basic_text = '''Comment["ENTER: qft_big_endian"](0:"qs[0]", 1:"qs[1]")'''
        parsed = parser.quipper_model.parse(basic_text, start="statement")
        self.assertEqual(['Inputs', ':', ['0', ':', 'Qbit'], []], parsed)
