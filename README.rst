Quippy
======
Quippy is a parser for quantum circuit descriptions produces by Quipper_.
Specifically, Quipper can output an ASCII description of the circuit, which can then be parsed by Quippy.

Quippy provides a default parser in quippy.parser that will parse given text as::

    from quipper.parser import quipper_parser
    parsed = quipper_parser().parse(text)

The parsed format uses an `Abstract Syntax Tree`_ to represent the Quipper circuit.
It is also possible to directly parse to a nice Object representation of the circuit by using the QuipperTransformer provided in the transformer package::

    from quipper.parser import quipper_parser
    from quipper.transformer import QuipperTransformer, Start
    parsed::Start = quipper_parser().parse(text, transformer=QuipperTransformer())

The resulting parsed object will have as type a Start object which will make the structure of the parse tree much clearer.
We use the optional static typing provided in `PEP 484`_ to provide types for the returned objects,
this was included in Python 3.5 or higher.
Python 3.6 or higher is recommended.


.. _Quipper: https://www.mathstat.dal.ca/~selinger/quipper/
.. _Abstract Syntax Tree: https://en.wikipedia.org/wiki/Abstract_syntax_tree
.. _PEP 484: https://www.python.org/dev/peps/pep-0484/
