from pathlib import Path
from unittest import TestCase

import _parser

ADDER_FILE = Path("resources") / "optimizer" / "Arithmetic_and_Toffoli" / "adder_8_before"


class TestParser(TestCase):
    def setUp(self):
        self.parser = _parser.QuipperParser()

    def test_arity(self):
        basic_text = """0:Qbit"""
        parsed = self.parser.parse(basic_text, rule_name="arity")
        self.assertEqual(1, len(parsed))
        self.assertEqual('0', parsed[0]['number'])

    def test_start(self):
        basic_text = """Inputs: 0:Qbit, 1:Cbit
        Outputs: 0:Qbit, 1:Cbit
        """
        parsed = self.parser.parse(basic_text, rule_name="circuit")
        self.assertEqual(2, len(parsed['inputs']))
        self.assertEqual(0, len(parsed['gatelist']))
        self.assertEqual(2, len(parsed['outputs']))
        self.assertEqual('0', parsed['inputs'][0]['number'])
        self.assertEqual('Qbit', parsed['inputs'][0]['type'])
        self.assertEqual('1', parsed['outputs'][1]['number'])
        self.assertEqual('Cbit', parsed['outputs'][1]['type'])

    def test_gatelist_qgate(self):
        basic_text = '''QGate["not"](0) with controls=[+2,-3] with nocontrol'''
        parsed = self.parser.parse(basic_text, rule_name="gate")
        self.assertEqual('not', parsed['name'])
        self.assertEqual(None, parsed['inverse'])
        self.assertEqual(2, len(parsed['controlled']['controls']))
        self.assertEqual('+2', parsed['controlled']['controls'][0])
        self.assertEqual('-3', parsed['controlled']['controls'][1])

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
        self.assertEqual("QInit1", parsed["state"])
        self.assertEqual('0', parsed["wire"]["qubit"])

    def test_sub_call_x1(self):
        text = '''Subroutine["SP", shape "([Q,Q,Q],())"] (3,4,5) -> (0,1,2) with controls=[+5] with nocontrol'''
        parsed = self.parser.parse(text, rule_name="subroutine_call")
        self.assertEqual(None, parsed["repetitions"])
        self.assertEqual("SP", parsed["name"])
        self.assertEqual("([Q,Q,Q],())", parsed["shape"])
        self.assertEqual(['3', '4', '5'], parsed['inputs'])
        self.assertEqual(['0', '1', '2'], parsed['outputs'])

    def test_sub_call_x154(self):
        text = '''Subroutine(x154)["SP", shape "([Q,Q,Q],())"] (3,4,5) -> (0,1,2)'''
        parsed = self.parser.parse(text, rule_name="subroutine_call")
        self.assertEqual("154", parsed["repetitions"])
        self.assertEqual("SP", parsed["name"])
        self.assertEqual("([Q,Q,Q],())", parsed["shape"])
        self.assertEqual(['3', '4', '5'], parsed['inputs'])
        self.assertEqual(['0', '1', '2'], parsed['outputs'])
