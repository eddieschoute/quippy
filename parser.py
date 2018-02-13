from qiskit.dagcircuit import DAGCircuit
import grammar

def parse(text: str):
    return grammar.quipper_model.parse(text, start="start")