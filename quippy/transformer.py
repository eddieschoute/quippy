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
        ty = TypeAssignment.Type.Qbit if t[1] == 'Qbit' else TypeAssignment.Type.Cbit
        return TypeAssignment(t[0], ty)

    def arity(self, t):
        return list(t)

    def qgate(self, t):
        ops = QGate.Op
        n = t[0]
        op: QGate.Op
        if n == "not":
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
            raise RuntimeError(f"Unknown QGate operation: {n}")

        return QGate(op=op, inverted=len(t[1].children) > 0, wire=t[2], control=t[3])

    def qrot(self, t):
        ops = QRot.Op
        n = t[0]
        op: QRot.Op
        if n == "exp(-i%Z)":
            op = ops.ExpZt
        elif n == "R(2pi/%)":
            op = ops.R
        else:
            raise RuntimeError(f"Unkown QRot operation: {n}")

        return QRot(op=op, timestep=t[1], wire=t[2])

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
        return Comment(*t)

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
        controllable: Subroutine.Control
        if t[2] == "yes":
            controllable = Subroutine.Control.yes
        elif t[2] == "no":
            controllable = Subroutine.Control.no
        else:
            controllable = Subroutine.Control.classically

        return Subroutine(name=t[0], shape=t[1], controllable=controllable, circuit=t[3])

    def start(self, t):
        circuit = t.pop(0)
        return Start(circuit, list(t))


class Wire(NamedTuple):
    i: int


class Control(NamedTuple):
    controlled: List[Wire]
    no_control: bool


class TypeAssignment(NamedTuple):
    class Type(Enum):
        Qbit = enum.auto()
        Cbit = enum.auto()

    wire: Wire
    type: Type


class Gate(NamedTuple):
    pass


class QGate(Gate, NamedTuple):
    class Op(Enum):
        """Possible quantum gate operations

            See: Quipper/Monad.hs
        """
        Not = enum.auto()  # Pauli X
        H = enum.auto()  # Hadamard
        MultiNot = enum.auto()  # Multi-target not
        Y = enum.auto()  # Pauli Y
        Z = enum.auto()  # Pauli Z
        S = enum.auto()  # Clifford S
        T = enum.auto()  # Clifford T=√S
        E = enum.auto()  # Clifford Clifford /E/ = /H//S/³ω³ gate.
        Omega = enum.auto()  # Scalar ω = exp(iπ/4)
        V = enum.auto()   # V = √X
        Swap = enum.auto()
        W = enum.auto()  # W is self-inverse and diagonalizes the SWAP
        IX = enum.auto()  # iX

    op: Op
    inverted: bool
    wire: Wire
    control: Control


class QRot(Gate, NamedTuple):
    class Op(Enum):
        """Possible quantum rotation operations

            See: Quipper/Monad.hs
        """
        ExpZt = enum.auto()  # Apply an [exp −/iZt/] gate. The timestep /t/ is a parameter.
        R = enum.auto()  # Apply a rotation by angle 2π/i/\/2[sup /n/] about the /z/-axis.

    op: Op
    timestep: float
    wire: Wire


class QInit(Gate, NamedTuple):
    value: bool
    wire: Wire


class SubroutineCall(Gate, NamedTuple):
    repetitions: int
    name: str
    shape: str
    inverted: bool
    inputs: List[Wire]
    outputs: List[Wire]
    control: Control


class Comment(Gate, NamedTuple):
    comment: str
    wire_comments: List[Tuple[Wire, str]]


class Circuit(NamedTuple):
    inputs: List[TypeAssignment]
    gates: List[Gate]
    outputs: List[TypeAssignment]


class Subroutine(NamedTuple):
    class Control(Enum):
        yes = enum.auto()
        no = enum.auto()
        classically = enum.auto()

    name: str
    shape: str
    controllable: Control
    circuit: Circuit


class Start(NamedTuple):
    circuit: Circuit
    subroutines: List[Subroutine]
