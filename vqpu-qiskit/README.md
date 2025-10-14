This module provides seamless integration between Qiskit (Python) and the vQPU/QDK API, eliminating the need to import `qristal.core`. It replicates the functionality of Qiskit's `AerSimulator` objects, enabling users to transpile quantum circuits, submit jobs, and get results.

## Steps using qbbackend.py

**Note**: The vQPU/QDK port must be active.

1) Create a Python environment.
   
   `python3.11 -m venv venv`

2) Activate the environment.

   `source venv/bin/activate`

3) Install Qiskit in the environment.

   `pip install qiskit qiskit-aer requests`

4) Copy `qbbackend.py` to your working directory.

5) Create your Qiskit code or consider the example `ghz_qbbackend.py` for testing.


## How qbbackend works?

A minimal Qiskit approach uses objects from AerSimulator(), e.g.:

```
from qiskit_aer import AerSimulator

circuit = # Qiskit circuit

sim = AerSimulator()

job = sim.run(circuit, shots=1024) 
result = job.result()
counts = result.get_counts()
```

A minimal `qbbackend.py` approach uses similar objects. The class is called `QuantumBackend(qpu_url)`, e.g.:


```
from qbbackend import QuantumBackend

circuit = # Qiskit circuit or OpenQASM string

sim = QuantumBackend(qpu_url="http://localhost:8888") # qpu_url points to the vQPU/QDK port

job = sim.run(circuit, shots=1024) 
result = job.result()
counts = result.get_counts()
```

## Advanced features
   
- `circuit = sim.transpile(circuit=user_circuit, basis_gates=['u3', 'cx'])`

   - It transpiles your Qiskit circuit to the basis gates specified, e.g., `['u3', 'cx']`, and translates it to an OpenQASM string.

   - If you use `sim.transpile(circuit=user_circuit)` without specifying the `basis_gates`, it will use the default ones, i.e., `['rx','ry','cz']`. 

     Your code may look like:
  
     ```
     from qbbackend import QuantumBackend 
  
     sim = QuantumBackend(qpu_url="http://localhost:8888")
  
     user_circuit = # Your Qiskit circuit
     circuit = sim.transpile(circuit=user_circuit, basis_gates=['u3', 'cx'])
  
     job = sim.run(circuit, shots=1024) 
     result = job.result()
     counts = result.get_counts()
     ```
   - `sim.transpile()` is not required. For a default transpilation and translation you can directly run `sim.run()`.
   - `sim.transpile()` is optional. You can use instead the Qiskit methods `transpile()` and `dumps()`. Below we show both approaches:

     ```
     user_circuit = # Your Qiskit circuit
 
     # qbbackend approach
     circuit = sim.transpile(circuit=user_circuit, basis_gates=['u3', 'cx'])
 
     # Qiskit approach
     circuit = transpile(user_circuit, basis_gates=['u3', 'cx'])
     circuit = dumps(circuit) 
     ```

- `sim.run(circuit, shots=1024)`

   - If your input is a Qiskit circuit, it first transpiles the circuit using `['rx','ry','cz']` as basis gates, then it translates the circuit to an OpenQASM2 string, and last it runs the circuit.

   - If your input is an OpenQASM2 string, the transpilation and translation steps are ignored. It directly runs the circuit. Below we show an example:

     ```
     circuit = '''OPENQASM 2.0;
     include "qelib1.inc";
     qreg q[2];
     creg c[2];
     h q[0];
     cx q[0],q[1];
     measure q[0] -> c[0];
     measure q[1] -> c[1];'''

     job = sim.run(circuit, shots=1024)
     result = job.result()
     counts = result.get_counts()
     ```

