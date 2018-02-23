from pathlib import Path
from unittest import TestCase

import _parser

ADDER_FILE = Path("resources") / "optimizer" / "Arithmetic_and_Toffoli" / "adder_8_before"


class TestParser(TestCase):
    def setUp(self):
        self.parser = _parser.QuipperParser()

    def test_iostatement(self):
        basic_text = """0:Qbit"""
        parsed = self.parser.parse(basic_text, rule_name="arity")
        self.assertEqual(1, len(parsed))
        self.assertEqual(0, parsed[0]['number'])

    def test_start(self):
        basic_text = """Inputs: 0:Qbit, 1:Cbit
        Outputs: 0:Qbit, 1:Cbit
        """
        parsed = self.parser.parse(basic_text, rule_name="circuit")
        self.assertEqual(2, len(parsed['inputs']))
        self.assertEqual(0, len(parsed['gatelist']))
        self.assertEqual(2, len(parsed['outputs']))
        self.assertEqual(0, parsed['inputs'][0]['number'])
        self.assertEqual('Qbit', parsed['inputs'][0]['type'])
        self.assertEqual(1, parsed['output'][1]['number'])
        self.assertEqual('Cbit', parsed['output'][1]['type'])

    def test_gatelist_qgate(self):
        basic_text = '''QGate["not"](0) with controls=[+2] with nocontrol'''
        parsed = self.parser.parse(basic_text, rule_name="gate")
        self.assertEqual('not', parsed['name'])
        self.assertEqual(None, parsed['inverse'])
        self.assertEqual('2', parsed['controlled']['control']['qubit'])

    def test_wire(self):
        basic_text = '''0:"qs[0]"'''
        parsed = self.parser.parse(basic_text, rule_name="wire")
        self.assertEqual('qs[0]', parsed['text'])
        self.assertEqual('0', parsed['qubit'])

    def test_statement_comment(self):
        basic_text = '''Comment["ENTER: qft_big_endian"](0:"qs[0]", 1:"qs[1]")'''
        parsed = self.parser.parse(basic_text, rule_name="comment")
        self.assertEqual('ENTER: qft_big_endian', parsed['text'])
        self.assertEqual(2, len(parsed['wires']))
        self.assertEqual('0', parsed['wires'][0]['qubit'])
        self.assertEqual('qs[1]', parsed['wires'][1]['text'])

    def test_qinit_gate(self):
        text = '''QInit1(0:"qs[0]") with nocontrol'''
        parsed = self.parser.parse(text, rule_name="qinit")
        pass
