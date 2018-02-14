from unittest import TestCase
from pathlib import Path

import _parser
import tatsu

ADDER_FILE = Path("resources") / "optimizer" / "Arithmetic_and_Toffoli" / "adder_8_before"

class TestParser(TestCase):
    def setUp(self):
        self.parser = _parser.QuipperParser()

    def test_iostatement(self):
        basic_text = """Inputs: 0:Qbit"""
        parsed = self.parser.parse(basic_text, rule_name="iostatement")
        self.assertEqual(1, len(parsed['qubits']))
        self.assertEqual('0', parsed['qubits'][0]['qubit'])

    def test_start(self):
        basic_text = """Inputs: 0:Qbit, 1:Qbit
        Outputs: 0:Qbit, 1:Qbit"""
        parsed = self.parser.parse(basic_text, rule_name="start")
        self.assertEqual(2, len(parsed['input']['qubits']))
        self.assertEqual(0, len(parsed['statements']))
        self.assertEqual(2, len(parsed['output']['qubits']))
        self.assertEqual('0', parsed['input']['qubits'][0]['qubit'])
        self.assertEqual('1', parsed['input']['qubits'][1]['qubit'])

    def test_statement_qgate(self):
        basic_text = '''QGate["not"](0) with controls=[+2] with nocontrol'''
        parsed = self.parser.parse(basic_text, rule_name="statement")
        self.assertEqual('"not"', parsed['name'])  #TODO: Fix the string parsing
        self.assertEqual(None, parsed['inverse'])
        self.assertEqual('2', parsed['controlled']['control']['qubit'])

    def test_wire(self):
        basic_text = '''0:"qs[0]"'''
        parsed = self.parser.parse(basic_text, rule_name="wire")
        self.assertEqual('"qs[0]"', parsed['text'])
        self.assertEqual('0', parsed['qubit'])

    def test_statement_comment(self):
        basic_text = '''Comment["ENTER: qft_big_endian"](0:"qs[0]", 1:"qs[1]")'''
        parsed = self.parser.parse(basic_text, rule_name="comment")
        self.assertEqual('"ENTER: qft_big_endian"', parsed['text'])
        self.assertEqual(2, len(parsed['wires']))
        self.assertEqual('0', parsed['wires'][0]['qubit'])
        self.assertEqual('"qs[1]"', parsed['wires'][1]['text'])
