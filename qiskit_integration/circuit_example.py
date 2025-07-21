import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.qasm2 import dumps
import warnings

import qristal.core

#Warn user if running a different qiskit version
required_qiskit_version = "1.2.0"
if qiskit.__version__ != required_qiskit_version:
    warnings.warn(f"Expected qiskit version 1.2.0 but running {qiskit.__version__}!")

# Step 1: Set up qiskit circuit 
circuit = QuantumCircuit(4)
circuit.h(0)
for q in range(3):
    circuit.cx(q, q+1)
circuit.measure_all()
print("Circuit:")
print(circuit)

# Step 2: Convert to OpenQasm2
#optional: transpile to QB native gate set
circuit = transpile(circuit, basis_gates=['rx', 'ry', 'cz'], optimization_level=3)
qasm_str = dumps(circuit)

# Step 3: Build qristal session
sim = qristal.core.session()
sim.acc = "aer"
sim.qn = 4
sim.sn = 1000

# Step 4: Run through qristal
sim.instring = qasm_str
sim.run()
print("Results:")
print(sim.results)
