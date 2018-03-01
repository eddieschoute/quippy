import glob
from pathlib import Path
import unittest
from unittest import TestCase

from lark import Tree
from lark.common import UnexpectedToken

from quipper_parser import quipper_parser

ADDER_FILE = Path("resources") / "optimizer" / "Arithmetic_and_Toffoli" / "adder_8_before"


class TestParser(TestCase):
    def test_arity(self):
        basic_text = """0:Qbit
        """
        parser = quipper_parser(start='arity')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('arity', [
            Tree('type_assignment', [
                Tree('int', ['0']),
                'Qbit'
                ]),
            ]), parsed)

    def test_circuit(self):
        basic_text = """Inputs: 0:Qbit, 1:Cbit
        Outputs: 0:Qbit, 1:Cbit
        """
        parser = quipper_parser(start='circuit')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('circuit', [
            Tree('arity', [
                Tree('type_assignment', [
                    Tree('int', ['0']),
                    'Qbit'
                    ]),
                Tree('type_assignment', [
                    Tree('int', ['1']),
                    'Cbit'
                    ]),
                ]),
            Tree('arity', [
                Tree('type_assignment', [
                    Tree('int', ['0']),
                    'Qbit'
                    ]),
                Tree('type_assignment', [
                    Tree('int', ['1']),
                    'Cbit'
                    ]),
                ])
            ]), parsed)

    def test_qgate(self):
        text = '''QGate["not"](0) with controls=[+2,-3] with nocontrol'''
        parser = quipper_parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('qgate', [
            Tree('string', ['"not"']),
            Tree('int', ["0"]),
            Tree('control_app', [
                Tree('int_list', [
                    Tree('int', ["+2"]),
                    Tree('int', ["-3"])
                    ]),
                "with nocontrol"
                ])
            ]), parsed)

    def test_wire(self):
        basic_text = '''0:"qs[0]"'''
        parser = quipper_parser(start='wire')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('wire', [
            Tree('int', ["0"]),
            Tree('string', ['"qs[0]"'])
            ]), parsed)

    def test_statement_comment(self):
        basic_text = '''Comment["ENTER: qft_big_endian"](0:"qs[0]", 1:"qs[1]")'''
        parser = quipper_parser(start='gate')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('comment', [
            Tree('string', ['"ENTER: qft_big_endian"']),
            Tree('wire_list', [
                Tree('wire', [
                    Tree('int', ['0']),
                    Tree('string', ['"qs[0]"'])
                    ]),
                Tree('wire', [
                    Tree('int', ['1']),
                    Tree('string', ['"qs[1]"'])
                    ])
                ])
            ]), parsed)

    def test_qinit_gate(self):
        text = '''QInit1(0:"qs[0]") with nocontrol'''
        parser = quipper_parser('gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('qinit', [
            'QInit1',
            Tree('wire', [
                Tree('int', ["0"]),
                Tree('string', ['"qs[0]"'])
                ]),
            "with nocontrol"
            ]), parsed)

    def test_sub_call_x1(self):
        text = '''Subroutine["SP", shape "([Q,Q,Q],())"] (3,4,5) -> (0,1,2) with controls=[+5] with nocontrol'''
        parser = quipper_parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('subroutine_call', [
            Tree('string', ['"SP"']),
            Tree('string', ['"([Q,Q,Q],())"']),
            Tree('int_list', [
                Tree('int', ["3"]),
                Tree('int', ["4"]),
                Tree('int', ["5"])
                ]),
            Tree('int_list', [
                Tree('int', ["0"]),
                Tree('int', ["1"]),
                Tree('int', ["2"])
                ]),
            Tree('control_app', [
                Tree('int_list', [
                    Tree('int', ["+5"])
                    ]),
                "with nocontrol"
                ])
            ]), parsed)

    def test_sub_call_x154(self):
        text = '''Subroutine(x154)["SP", shape "([Q,Q,Q],())"] (3,4,5) -> (0,1,2)'''
        parser = quipper_parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('subroutine_call', [
            Tree('int', ["154"]),
            Tree('string', ['"SP"']),
            Tree('string', ['"([Q,Q,Q],())"']),
            Tree('int_list', [
                Tree('int', ["3"]),
                Tree('int', ["4"]),
                Tree('int', ["5"])
                ]),
            Tree('int_list', [
                Tree('int', ["0"]),
                Tree('int', ["1"]),
                Tree('int', ["2"])
                ]),
            Tree('control_app', [])
            ]), parsed)

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
        parser = quipper_parser(start='subroutine')
        parsed = parser.parse(text)
        # Break the equality check into two steps because it is too big.
        circuit = parsed.children[3]
        circuit_tree = Tree('circuit', [
            Tree('arity', [
                Tree('type_assignment', [
                    Tree('int', ['0']),
                    'Qbit'
                    ])
                ]),
            Tree('qgate', [
                Tree('string', ['"H"']),
                '*',
                Tree('int', ['0']),
                Tree('control_app', [
                    Tree('int_list', [
                        Tree('int', ['+3']),
                        Tree('int', ['-5']),
                        Tree('int', ['-6'])
                        ]),
                    'with nocontrol'
                    ])
                ]),
            Tree('qrot', [
                Tree('string', ['"bla"']),
                Tree('float', ['1e-05']),
                Tree('int', ['1'])
                ]),
            Tree('arity', [
                Tree('type_assignment', [
                    Tree('int', ['0']),
                    'Qbit'
                    ])
                ]),
            ])
        self.assertEqual(circuit_tree, circuit)
        self.assertEqual(Tree('subroutine', [
            Tree('string', ['"S1"']),
            Tree('string', ['"([Q],())"']),
            'yes',
            circuit_tree
            ]), parsed)

    @unittest.skip
    def test_optimizer(self):
        """Try to parse all files in the optimizer resource folder."""
        optimizer_files_path = Path("resources") / "optimizer" / "**"
        optimizer_files = glob.glob(str(optimizer_files_path), recursive=True)
        quipper_paths = filter(lambda path: not path.is_dir()
                                            and path.suffix == '',
                               map(lambda s: Path(s), optimizer_files))
        parser = quipper_parser()
        for path in quipper_paths:
            print(path)
            with open(path) as quipper_file:
                try:
                    parser.parse(quipper_file.read())
                except UnexpectedToken as e:
                    raise RuntimeError(f"Failed to parse {path}. Error: {e}")
