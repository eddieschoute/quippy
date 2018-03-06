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

import glob
import logging
from pathlib import Path
import unittest
from unittest import TestCase

from lark import Tree
from lark.common import UnexpectedToken

from quippy.parser import quipper_parser

logger = logging.getLogger(__name__)


class TestParser(TestCase):
    def parser(self, start='start'):
        return quipper_parser(start=start, transformer=None)

    def test_arity(self):
        basic_text = """0:Qbit
        """
        parser = self.parser(start='arity')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('arity', [
            Tree('type_assignment', [
                Tree('wire', [Tree('int', ['0'])]),
                'Qbit'
                ]),
            ]), parsed)

    def test_circuit(self):
        basic_text = """Inputs: 0:Qbit, 1:Cbit
        Outputs: 0:Qbit, 1:Cbit
        """
        parser = self.parser(start='circuit')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('circuit', [
            Tree('arity', [
                Tree('type_assignment', [
                    Tree('wire', [Tree('int', ['0'])]),
                    'Qbit'
                    ]),
                Tree('type_assignment', [
                    Tree('wire', [Tree('int', ['1'])]),
                    'Cbit'
                    ]),
                ]),
            Tree('arity', [
                Tree('type_assignment', [
                    Tree('wire', [Tree('int', ['0'])]),
                    'Qbit'
                    ]),
                Tree('type_assignment', [
                    Tree('wire', [Tree('int', ['1'])]),
                    'Cbit'
                    ]),
                ])
            ]), parsed)

    def test_qgate(self):
        text = '''QGate["not"](0) with controls=[+2,-3] with nocontrol'''
        parser = self.parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('qgate', [
            Tree('string', ['"not"']),
            Tree('inversion', []),
            Tree('wire', [Tree('int', ["0"])]),
            Tree('control_app', [
                Tree('wire_list', [
                    Tree('wire', [Tree('int', ["+2"])]),
                    Tree('wire', [Tree('int', ["-3"])])
                    ]),
                "with nocontrol"
                ])
            ]), parsed)

    def test_statement_comment(self):
        basic_text = '''Comment["ENTER: qft_big_endian"](0:"qs[0]", 1:"qs[1]")'''
        parser = self.parser(start='gate')
        parsed = parser.parse(basic_text)
        self.assertEqual(Tree('comment', [
            Tree('string', ['"ENTER: qft_big_endian"']),
            Tree('wire_string_list', [
                Tree('wire', [Tree('int', ['0'])]),
                Tree('string', ['"qs[0]"']),
                Tree('wire', [Tree('int', ['1'])]),
                Tree('string', ['"qs[1]"'])
                ])
            ]), parsed)

    def test_qinit_gate(self):
        text = '''QInit1(0) with nocontrol'''
        parser = self.parser('gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('qinit', [
            'QInit1',
            Tree('wire', [Tree('int', ["0"])]),
            "with nocontrol"
            ]), parsed)

    def test_sub_call_x1(self):
        text = '''Subroutine["SP", shape "([Q,Q,Q],())"] (3,4,5) -> (0,1,2) with controls=[+5] with nocontrol'''
        parser = self.parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('subroutine_call', [
            Tree('string', ['"SP"']),
            Tree('string', ['"([Q,Q,Q],())"']),
            Tree('inversion', []),
            Tree('wire_list', [
                Tree('wire', [Tree('int', ["3"])]),
                Tree('wire', [Tree('int', ["4"])]),
                Tree('wire', [Tree('int', ["5"])])
                ]),
            Tree('wire_list', [
                Tree('wire', [Tree('int', ["0"])]),
                Tree('wire', [Tree('int', ["1"])]),
                Tree('wire', [Tree('int', ["2"])])
                ]),
            Tree('control_app', [
                Tree('wire_list', [
                    Tree('wire', [Tree('int', ["+5"])])
                    ]),
                "with nocontrol"
                ])
            ]), parsed)

    def test_sub_call_x154(self):
        text = '''Subroutine(x154)["SP", shape "([Q,Q,Q],())"] (3,4,5) -> (0,1,2)'''
        parser = self.parser(start='gate')
        parsed = parser.parse(text)
        self.assertEqual(Tree('subroutine_call', [
            Tree('int', ["154"]),
            Tree('string', ['"SP"']),
            Tree('string', ['"([Q,Q,Q],())"']),
            Tree('inversion', []),
            Tree('wire_list', [
                Tree('wire', [Tree('int', ["3"])]),
                Tree('wire', [Tree('int', ["4"])]),
                Tree('wire', [Tree('int', ["5"])])
                ]),
            Tree('wire_list', [
                Tree('wire', [Tree('int', ["0"])]),
                Tree('wire', [Tree('int', ["1"])]),
                Tree('wire', [Tree('int', ["2"])])
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
        parser = self.parser(start='subroutine')
        parsed = parser.parse(text)
        # Break the equality check into two steps because it is too big.
        circuit = parsed.children[3]
        circuit_tree = Tree('circuit', [
            Tree('arity', [
                Tree('type_assignment', [
                    Tree('wire', [Tree('int', ['0'])]),
                    'Qbit'
                    ])
                ]),
            Tree('qgate', [
                Tree('string', ['"H"']),
                Tree('inversion', ['*']),
                Tree('wire', [Tree('int', ['0'])]),
                Tree('control_app', [
                    Tree('wire_list', [
                        Tree('wire', [Tree('int', ['+3'])]),
                        Tree('wire', [Tree('int', ['-5'])]),
                        Tree('wire', [Tree('int', ['-6'])])
                        ]),
                    'with nocontrol'
                    ])
                ]),
            Tree('qrot', [
                Tree('string', ['"bla"']),
                Tree('float', ['1e-05']),
                Tree('wire', [Tree('int', ['1'])])
                ]),
            Tree('arity', [
                Tree('type_assignment', [
                    Tree('wire', [Tree('int', ['0'])]),
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
        optimizer_files_path = Path(__file__).parents[1] / "resources" / "optimizer" / "**"
        optimizer_files = glob.glob(str(optimizer_files_path), recursive=True)
        quipper_paths = filter(lambda path: not path.is_dir()
                                            and path.suffix == '',
                               map(lambda s: Path(s), optimizer_files))
        parser = self.parser()
        for path in quipper_paths:
            print(path)
            with open(path) as quipper_file:
                try:
                    parser.parse(quipper_file.read())
                except UnexpectedToken as e:
                    raise RuntimeError(f"Failed to parse {path}. Error: {e}")

    @unittest.skip
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
        for path in quipper_paths:
            print(path)
            with open(path) as quipper_file:
                try:
                    parser.parse(quipper_file.read())
                except UnexpectedToken as e:
                    raise RuntimeError(f"Failed to parse {path}. Error: {e}")
