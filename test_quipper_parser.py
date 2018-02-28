from pathlib import Path
from unittest import TestCase

from lark import Tree

from quipper_parser import quipper_parser

ADDER_FILE = Path("resources") / "optimizer" / "Arithmetic_and_Toffoli" / "adder_8_before"


class TestParser(TestCase):
    def test_arity(self):
        basic_text = """0:Qbit"""
        parser = quipper_parser(start='arity')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('type_assignment', ['0', 'Qbit']), parsed)

    def test_circuit(self):
        basic_text = """Inputs: 0:Qbit, 1:Cbit
        Outputs: 0:Qbit, 1:Cbit
        """
        parser = quipper_parser(start='circuit')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('circuit', [
            Tree('arity', [
                Tree('type_assignment', ['0', 'Qbit']),
                Tree('type_assignment', ['1', 'Cbit']),
                '\n'
                ]),
            Tree('arity', [
                Tree('type_assignment', ['0', 'Qbit']),
                Tree('type_assignment', ['1', 'Cbit']),
                '\n'
                ])
            ]), parsed)

    def test_gatelist_qgate(self):
        basic_text = '''QGate["not"](0) with controls=[+2,-3] with nocontrol'''
        parser = quipper_parser(start='gate')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('qgate', [
            '"not"',
            "0",
            Tree('control_app', [
                Tree('controlled', [
                    "+2",
                    "-3"
                    ]),
                "with nocontrol"
                ])
            ]), parsed)

    def test_wire(self):
        basic_text = '''0:"qs[0]"'''
        parser = quipper_parser(start='wire')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('wire', [
            "0",
            '"qs[0]"'
            ]), parsed)

    def test_statement_comment(self):
        basic_text = '''Comment["ENTER: qft_big_endian"](0:"qs[0]", 1:"qs[1]")'''
        parser = quipper_parser(start='gate')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('comment', [
            '"ENTER: qft_big_endian"',
            Tree('wire', ['0', '"qs[0]"']),
            Tree('wire', ['1', '"qs[1]"'])
            ]), parsed)

    def test_qinit_gate(self):
        text = '''QInit1(0:"qs[0]") with nocontrol'''
        parser = quipper_parser('gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('qinit', [
            "1",
            Tree('wire', [
                "0",
                '"qs[0]"'
                ]),
            "with nocontrol"
            ]), parsed)

    def test_sub_call_x1(self):
        text = '''Subroutine["SP", shape "([Q,Q,Q],())"] (3,4,5) -> (0,1,2) with controls=[+5] with nocontrol'''
        parser = quipper_parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('subroutine_call', [
            '"SP"',
            '"([Q,Q,Q],())"',
            Tree('int_list', ["3","4","5"]),
            Tree('int_list', ["0","1","2"]),
            Tree('control_app', [
                Tree('int_list', ["+5"]),
                "with nocontrol"
                ])
            ]), parsed)

    def test_sub_call_x154(self):
        text = '''Subroutine(x154)["SP", shape "([Q,Q,Q],())"] (3,4,5) -> (0,1,2)'''
        parser = quipper_parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('subroutine_call', [
            "154",
            '"SP"',
            '"([Q,Q,Q],())"',
            Tree('int_list', ["3","4","5"]),
            Tree('int_list', ["0","1","2"]),
            Tree('control_app', [])
            ]), parsed)
