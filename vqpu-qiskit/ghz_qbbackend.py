from qbbackend import QuantumBackend
from qiskit import QuantumCircuit

# Parameters
num_qubits = 10
shots = 1024

# Step 1: Build your Qiskit circuit
ghz = QuantumCircuit(num_qubits, num_qubits)
ghz.h(0)
for i in range(num_qubits - 1):
    ghz.cx(i, i + 1)
ghz.measure(range(num_qubits), range(num_qubits))

# Step 2: Set the backend and transpile the circuit
print("Setting backend...")
sim = QuantumBackend(qpu_url="http://localhost:8888")

print("Transpiling circuit...")
circuit = sim.transpile(circuit=ghz)

# Step 3: Submit the circuit
print("Submitting circuit...")
job = sim.run(circuit, shots=1024)

# Step 4: Get results
print("Getting results...")
result = job.result()
counts = result.get_counts()
print(f"The counts from the API are: \n{counts}")
