// The root of any program
start : circuit subroutine* NEWLINE

circuit : "Inputs:" arity (gate NEWLINE)* "Outputs:" arity

subroutine : NEWLINE "Subroutine:" STRING NEWLINE "Shape:" STRING NEWLINE "Controllable:" SUB_CONTROL NEWLINE circuit
SUB_CONTROL : "yes"
    | "no"
    | "classically"


// Wires and their types
arity : type_assignment ("," type_assignment)* NEWLINE
type_assignment : INT ":" TYPE
TYPE: "Qbit"
    | "Cbit"

// Gate control
control_app : [controlled] [NO_CONTROL]
?controlled : "with controls=[" int_list "]"
NO_CONTROL : "with nocontrol"

// All gates
?gate : qgate
    | qrot
    | gphase
    | cnot
    | cgate
    | cswap
    | qprep
    | qunprep
    | qinit
    | cinit
    | cterm
    | qmeas
    | qdiscard
    | cdiscard
    | dterm
    | subroutine_call
    | comment

// Gate definitions
qgate       : "QGate[" STRING "]" ["*"] "(" INT ")" control_app
qrot        : "QRot[" STRING "," FLOAT "](" INT ")"
gphase      : "Gphase() with t=" FLOAT control_app "with anchors=[" wire_list "]"
cnot        : "CNot(" wire ")" control_app
cgate       : "CGate[" STRING "]" ["*"] "(" wire_list ")" [NO_CONTROL]
cswap       : "CSwap(" wire "," wire ")" control_app
qprep       : "QPrep(" wire ")" [NO_CONTROL]
qunprep     : "QUnprep(" wire ")" [NO_CONTROL]
qinit       : "QInit" ZERO_ONE "(" wire ")" [NO_CONTROL]
cinit       : "CInit" ZERO_ONE "(" wire ")" [NO_CONTROL]
qterm       : "QTerm" ZERO_ONE "(" wire ")" [NO_CONTROL]
cterm       : "CTerm" ZERO_ONE "(" wire ")" [NO_CONTROL]
qmeas       : "QMeas(" wire ")"
qdiscard    : "QDiscard(" wire ")"
cdiscard    : "CDiscard(" wire ")"
dterm       : "DTerm" ZERO_ONE "(" wire ")"
subroutine_call : "Subroutine" ["(x" INT ")"] "[" STRING ", shape" STRING "]" ["*"] "(" int_list ") -> (" int_list ")" control_app
comment : "Comment[" STRING "](" wire_list ")"
// Make node for list to disambiguate if needed.
wire_list: wire ("," wire)*
int_list : INT ("," INT)*

ZERO_ONE : "0"
    | "1"

// Reference to an input wire and a textual description
wire : INT ":" STRING

// Newlines are significant
%import common.WS_INLINE -> WS
%ignore WS
%import common.NEWLINE -> NEWLINE
%import common.ESCAPED_STRING -> STRING
%import common.SIGNED_FLOAT -> FLOAT
%import common.SIGNED_INT -> INT
