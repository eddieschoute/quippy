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

from lark import Lark
from pkg_resources import resource_string

from quippy.transformer import QuipperTransformer

"""The grammar is imported from the quipper file as a string."""
GRAMMAR = resource_string(__name__, 'quipper.g').decode()


def quipper_parser(start='start', parser='lalr', transformer=QuipperTransformer(), **kwargs
                   ) -> Lark:
    """Construct a parser for the Quipper grammar.

    :param start: the rule in the grammar to start parsing at.
    :param parser: the type of Lark parser to use.
    :param kwargs: Further options to pass to Lark.
    :param transformer: The lark.transformer.Transformer instance that transforms ASTs
        to python objects. By default 'QuipperTransformer()'.
    :return: A Lark parser object that .parse can be called on.
    """
    return Lark(GRAMMAR, start=start, parser=parser, transformer=transformer, **kwargs)
