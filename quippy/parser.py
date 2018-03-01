from pathlib import Path
from lark import Lark

GRAMMAR_FILE = Path(__file__).parent / "quipper.g"

def quipper_parser(start='start', parser='lalr', **kwargs) -> Lark:
    grammar = GRAMMAR_FILE.read_text()
    return Lark(grammar, start=start, parser=parser, **kwargs)
