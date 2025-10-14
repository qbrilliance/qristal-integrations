import qbqpu

qasm_str = '''OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];'''

circuit = qasm_str.split("\n")
shots = 1024
qpu_url="http://localhost:8080" # vQPU/QDK port

print(f"Submitting circuit to {qpu_url}.")
response = qbqpu.run_experiment(circuit, shots, qpu_url)
counts=qbqpu.get_bitstring_counts(response)
print(f"The counts from the vQPU are: \n{counts}")
