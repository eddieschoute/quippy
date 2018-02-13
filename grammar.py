import tatsu.grammars

GRAMMAR = '''
@@grammar :: quipper
@@whitespace :: /[^\S\n]*/

start :: Program = input:iostatement newline statements:{statement newline} ouput:iostatement $ ;

iostatement :: IOStatement = ("Inputs"|"Outputs")":" qubits:",".{ioqubit}+ ;
ioqubit = qubit:int ":" "Qbit" ;

statement
    =
    | qgate
    | qrot
    | comment
    ;

qgate :: QGate = "QGate[" ~ name:string "]" inverse:["*"] "(" qubit:int ") with" control:(controlled | no_control) ;
qrot :: QRot = "QRot[" ~ string "," double "](" int ")" ;

comment :: Comment = "Comment[" ~ string "](" ",".{wire}+ ")" ;
wire = int ":" string ;

controlled :: Controlled = "controls=[" control:control "] with nocontrol" ;
no_control :: NoControl = "nocontrol" ;

control
    =
    | "-" int
    | "+" int
    ;

string = /"\S+"/ ;
int = /\d+/ ;
double = /(-)?\d+\.\d+e(-)?\d\d/ ;
newline = /\n/ ;

'''

quipper_model: tatsu.grammars.Grammar = tatsu.compile(GRAMMAR)
