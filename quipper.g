// The root of any program
start : circuit subroutine* NEWLINE* // Allow trailing newlines

circuit : "Inputs:" arity (gate NEWLINE)* "Outputs:" arity

subroutine: NEWLINE "Subroutine:" STRING NEWLINE "Shape:" STRING NEWLINE "Controllable:" SUB_CONTROL NEWLINE circuit
SUB_CONTROL : "yes"
    | "no"
    | "classically"

// Wires and their types
arity : type_assignment ("," type_assignment)* NEWLINE
type_assignment : INT ":" TYPE
TYPE: "Qbit"
    | "Cbit"

// Gate control
control_app : controlled? NO_CONTROL?
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
qgate       : "QGate[" STRING "]" "*"? "(" INT ")" control_app
qrot        : "QRot[" STRING "," FLOAT "]" "(" INT ")"
gphase      : "Gphase() with t=" FLOAT control_app "with anchors=[" wire_list "]"
cnot        : "CNot(" wire ")" control_app
cgate       : "CGate[" STRING "]" "*"? "(" wire_list ")" NO_CONTROL?
cswap       : "CSwap(" wire "," wire ")" control_app
qprep       : "QPrep(" wire ")" NO_CONTROL?
qunprep     : "QUnprep(" wire ")" NO_CONTROL?
qinit       : QINIT_STATE "(" wire ")" NO_CONTROL?
// for the lexer we cannot factor out a "0" or "1" string due to ambiguities with INT
QINIT_STATE : "QInit0" | "QInit1"
cinit       :  CINIT_STATE "(" wire ")" NO_CONTROL?
CINIT_STATE : "CInit0" | "CInit1"
qterm       : QTERM_STATE "(" wire ")" NO_CONTROL?
QTERM_STATE : "QTerm0" | "QTerm1"
cterm       : CTERM_STATE "(" wire ")" NO_CONTROL?
CTERM_STATE : "CTerm0" | "CTerm1"
qmeas       : "QMeas(" wire ")"
qdiscard    : "QDiscard(" wire ")"
cdiscard    : "CDiscard(" wire ")"
dterm       : DTERM_STATE "(" wire ")"
DTERM_STATE : "DTerm0" | "DTerm1"
subroutine_call : "Subroutine" ["(x" INT ")"] "[" STRING ", shape" STRING "]" "*"? "(" int_list ") -> (" int_list ")" control_app
// Note: ] and ( have to be separate tokens for the lexer.
comment : "Comment[" STRING "]" "(" wire_list ")"
// Make node for list to disambiguate if needed.
wire_list: wire ("," wire)*
int_list : INT ("," INT)*

// Reference to an input wire and a textual description
wire : INT ":" STRING

// Newlines are significant
%import common.WS_INLINE -> WS
%ignore WS
%import common.CR
%import common.LF
NEWLINE: (CR? LF)  // Only match a single newline
%import common.ESCAPED_STRING -> STRING
%import common.SIGNED_FLOAT
FLOAT.3 : SIGNED_FLOAT
%import common.SIGNED_INT
INT.2 : SIGNED_INT
