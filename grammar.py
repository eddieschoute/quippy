import tatsu

GRAMMAR = '''
@@grammar :: quipper
@@whitespace :: /[^\S\n]*/

start = iostatement {statement} iostatement $ ;

iostatement = ("Inputs"|"Outputs")":" ioqubit {"," ioqubit} ;
ioqubit = int ":" "Qbit" ;

statement
    =
    | qgate
    | qrot
    | comment
    ;

qgate = "QGate[" string "]" ["*"] "(" int ") with" control_app ;
qrot = "QRot[" string "," double "](" int ")" ;

comment = "Comment[" string "](" wire {"," wire}* ")" ;
wire = int ":" string ;

control_app
    =
    | "nocontrol"
    | "controls=[" control "] with nocontrol"
    ;

control
    =
    | "-" int
    | "+" int
    ;

string = /"\S+"/ ;
int = /\d+/ ;
double = /(-)?\d+\.\d+e(-)?\d\d/ ;

'''

quipper_model = tatsu.compile(GRAMMAR)
