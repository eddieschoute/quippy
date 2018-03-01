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

    wire_list = list
    int_list = list

    def type_assignment(self, t):
        ty = TypeAssignment.Type.Qbit if t[1] == 'Qbit' else TypeAssignment.Type.Cbit
        return TypeAssignment(t[0], ty)

    def arity(self, t):
        return list(t)

    def qgate(self, t):
        if t[1] == "*":
            return QGate(name=t[0], inverted=True, wire=t[2], control=t[3])
        else:
            return QGate(name=t[0], inverted=False, wire=t[1], control=t[2])

    def qrot(self, t):
        return QRot(*t)

    def control_app(self, t):
        if not t:
            return Control(list(), False)

        if len(t) == 2:
            return Control(controlled=t[0], no_control=True)

        if t[0] == "with nocontrol":
            return Control(controlled=list(), no_control=True)

        return Control(controlled=list(t[0]), no_control=False)

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


class Control(NamedTuple):
    controlled: List[int]
    no_control: bool


class TypeAssignment(NamedTuple):
    class Type(Enum):
        Qbit = enum.auto()
        Cbit = enum.auto()

    wire: int
    type: Type


class Gate(NamedTuple):
    pass


class QGate(Gate, NamedTuple):
    name: str
    inverted: bool
    wire: int
    control: Control


class QRot(Gate, NamedTuple):
    name: str
    timestep: float
    wire: int


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
