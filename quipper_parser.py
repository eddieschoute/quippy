from lark import Lark


def quipper_parser(start='hello_world', **kwargs) -> Lark:
    with open('quipper.g') as grammar_file:
        return Lark(grammar_file.read(), start=start, parser='lalr', **kwargs)
