all: _parser.py _model.py

_parser.py: grammar.ebnf
	tatsu grammar.ebnf > _parser.py

_model.py: grammar.ebnf
	tatsu -g grammar.ebnf > _model.py
