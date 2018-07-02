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

import enum
from enum import Enum
from typing import *

from lark import Transformer


class QuipperTransformer(Transformer):
    def int(self, t):
        return int(t[0])

    def float(self, t):
        return float(t[0])

    def string(self, t):
        return str(t[0][1:-1])

    def wire(self, t):
        return Wire(t[0])

    wire_list = list

    def wire_string_list(self, t):
        wires = (el for i, el in enumerate(t) if i % 2 == 0)
        labels = (el for i, el in enumerate(t) if i % 2 == 1)
        return list(zip(wires, labels))

    def type_assignment(self, t):
        ty = TypeAssignment_Type.Qbit if t[1] == 'Qbit' else TypeAssignment_Type.Cbit
        return TypeAssignment(t[0], ty)

    def arity(self, t):
        return list(t)

    def qgate(self, t):
        ops = QGate_Op
        n = t[0]
        op = None  # type: QGate_Op
        # "X" is used in simcount.
        if n == "not" or n == "x" or n == "X":
            op = ops.Not
        elif n == "H":
            op = ops.H
        elif n == "multinot":
            op = ops.MultiNot
        elif n == "Y":
            op = ops.Y
        elif n == "Z":
            op = ops.Z
        elif n == "S":
            op = ops.S
        elif n == "E":
            op = ops.E
        elif n == "T":
            op = ops.T
        elif n == "V":
            op = ops.V
        elif n == "swap":
            op = ops.Swap
        elif n == "omega":
            op = ops.Omega
        elif n == "iX":
            op = ops.IX
        else:
            raise RuntimeError("Unknown QGate operation: {}".format(n))

        return QGate(op=op, inverted=len(t[1].children) > 0, wire=t[2], control=t[3])

    def qrot(self, t):
        ops = QRot_Op
        n = t[0]
        op = None  # type: QRot.Op
        if n == "exp(-i%Z)":
            op = ops.ExpZt
        elif n == "R(2pi/%)":
            op = ops.R
        else:
            raise RuntimeError("Unkown QRot operation: {}".format(n))

        return QRot(
            op=op,
            timestep=t[1],
            inverted=len(t[2].children) > 0,
            wire=t[3]
            )

    def qinit(self, t):
        return QInit(value=True if t[0] == 'QInit1' else False, wire=t[1])

    def subroutine_call(self, t):
        repetitions = 1
        if isinstance(t[0], int):
            repetitions = t[0]
            t.pop(0)

        return SubroutineCall(
            repetitions=repetitions,
            name=t[0],
            shape=t[1],
            inverted=len(t[2].children) > 0,
            inputs=t[3],
            outputs=t[4],
            control=t[5]
            )

    def comment(self, t):
        wire_comments = t[2] if len(t) > 2 else None

        return Comment(
            comment=t[0],
            inverted=len(t[1].children) > 0,
            wire_comments=wire_comments
            )

    def control_app(self, t):
        if not t:
            return Control(list(), False)

        if len(t) == 2:
            return Control(controlled=t[0], no_control=True)

        if t[0] == "with nocontrol":
            return Control(controlled=list(), no_control=True)

        return Control(controlled=t[0], no_control=False)

    def circuit(self, t):
        return Circuit(inputs=t[0], gates=t[1:-1], outputs=t[-1])

    def subroutine(self, t):
        controllable = None  # type: Subroutine.Control
        if t[2] == "yes":
            controllable = Subroutine_Control.yes
        elif t[2] == "no":
            controllable = Subroutine_Control.no
        else:
            controllable = Subroutine_Control.classically

        return Subroutine(name=t[0], shape=t[1], controllable=controllable, circuit=t[3])

    def start(self, t):
        circuit = t.pop(0)
        return Start(circuit, list(t))


Wire = NamedTuple('Wire', [
    ('i', int)
    ])

Control = NamedTuple('Control', [
    ('controlled', List[Wire]),
    ('no_control', bool)
    ])


@enum.unique
class TypeAssignment_Type(Enum):
    Qbit = 1
    Cbit = 2


TypeAssignment = NamedTuple('TypeAssignment', [
    ('wire', Wire),
    ('type', TypeAssignment_Type)
    ])


class Gate:
    pass


@enum.unique
class QGate_Op(Enum):
    """Possible quantum gate operations

        See: Quipper/Monad.hs
    """
    Not = 1  # Pauli X
    H = 2  # Hadamard
    MultiNot = 3  # Multi-target not
    Y = 4  # Pauli Y
    Z = 5  # Pauli Z
    S = 6  # Clifford S
    T = 7  # Clifford T=√S
    E = 8  # Clifford Clifford /E/ = /H//S/³ω³ gate.
    Omega = 9  # Scalar ω = exp(iπ/4)
    V = 10  # V = √X
    Swap = 11
    W = 12  # W is self-inverse and diagonalizes the SWAP
    IX = 13  # iX


class QGate(Gate, NamedTuple('QGate', [
    ('op', QGate_Op),
    ('inverted', bool),
    ('wire', Wire),
    ('control', Control)
    ])):
    pass


@enum.unique
class QRot_Op(Enum):
    """Possible quantum rotation operations

        See: Quipper/Monad.hs
    """
    ExpZt = 1  # Apply an [exp −/iZt/] gate. The timestep /t/ is a parameter.
    R = 2  # Apply a rotation by angle 2π/i/\/2[sup /n/] about the /z/-axis.


class QRot(Gate, NamedTuple('QRot', [
    ('op', QRot_Op),
    ('inverted', bool),
    ('timestep', float),
    ('wire', Wire)
    ])):
    pass


class QInit(Gate, NamedTuple("QInit", [
    ("value", bool),
    ("wire", Wire)
    ])):
    pass


class SubroutineCall(Gate, NamedTuple("SubroutineCall", [
    ("repetitions", int),
    ("name", str),
    ("shape", str),
    ("inverted", bool),
    ("inputs", List[Wire]),
    ("outputs", List[Wire]),
    ("control", Control)
    ])):
    pass


class Comment(Gate, NamedTuple("Comment", [
    ("comment", str),
    ("inverted", bool),
    ("wire_comments", List[Tuple[Wire, str]])
    ])):
    pass


Circuit = NamedTuple("Circuit", [
    ("inputs", List[TypeAssignment]),
    ("gates", List[Gate]),
    ("outputs", List[TypeAssignment])
    ])


@enum.unique
class Subroutine_Control(Enum):
    yes = 1
    no = 2
    classically = 3


Subroutine = NamedTuple("Subroutine", [
    ("name", str),
    ("shape", str),
    ("controllable", Subroutine_Control),
    ("circuit", Circuit)
    ])

Start = NamedTuple("Start", [
    ("circuit", Circuit),
    ("subroutines", List[Subroutine])
    ])
