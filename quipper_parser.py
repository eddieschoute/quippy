from lark import Lark


def quipper_parser(start='start', parser='lalr', **kwargs) -> Lark:
    with open('quipper.g') as grammar_file:
        return Lark(grammar_file.read(), start=start, parser=parser, **kwargs)
