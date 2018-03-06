Quippy
======
Quippy is a parser for quantum circuit descriptions produces by Quipper_.
Specifically, Quipper can output an ASCII description of the circuit, which can then be parsed by Quippy.

Quippy provides a default parser in quippy.parser that will parse given text as::

    import quippy
    parsed::quippy.Start = quippy.parser().parse(text)

The parsed format uses an `quippy.Start` object to represent the Quipper circuit by default.
This is a nice Object representation of the circuit the `Abstract Syntax Tree`_ is
directly transformed to by `quippy.transformer.QuipperTransformer`.
The resulting parsed object will have as type a Start object which will make the structure of the parse tree much clearer.
If you do no wish to use the included transformer but would rather have a general AST then pass::

    quippy.parser(transformer=None)

We use the optional static typing provided in `PEP 484`_ to provide types for the returned objects,
this was included in Python 3.5 or higher.
Python 3.6 or higher is recommended.


.. _Quipper: https://www.mathstat.dal.ca/~selinger/quipper/
.. _Abstract Syntax Tree: https://en.wikipedia.org/wiki/Abstract_syntax_tree
.. _PEP 484: https://www.python.org/dev/peps/pep-0484/
