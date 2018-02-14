import tatsu.grammars

quipper_model: tatsu.grammars.Grammar = tatsu.compile(open("grammar.ebnf").read())


def parse(text: str):
    return quipper_model.quipper_model.parse(text, start="start")
