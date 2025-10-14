This module provides seamless integration between OpenQASM2 and the vQPU/QDK API, eliminating the need to import `qristal.core`. It facilitates direct transmission of JSON-formatted OpenQASM2 strings to the API, streamlining job submission and execution workflows.

## Steps using qbqpu.py

**Note**: The vQPU/QDK port must be active.

1) Create a Python environment.
   
   `python3.11 -m venv venv`

2) Activate the environment.

   `source venv/bin/activate`

3) Install HTTP requests in the environment.

   `pip install requests`

4) Copy `qbqpu.py` to your working directory.

5) Create your OpenQASM2 code or consider the example `qasm_example.py` for testing.


## How does it work?

The qcstack API provides an OpenQASM2 endpoint that can accept circuits
directly. `qbqpu.py` becomes the utility module that facilitates this interaction.

A minimal `qbqpu.py` approach:

```
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

response = qbqpu.run_experiment(circuit, shots=1024, qpu_url="http://localhost:8080") # qpu_url points to the vQPU/QDK port
counts=qbqpu.get_bitstring_counts(response)
```

## Advanced features

`qbqpu.py` entities:

- `send_experiment(circuit, shots, qpu_url)` accepts a circuit (string array) and shot count, and sends an experiment to the qcstack API at `qpu_url`. It returns the API response.

- `get_experiment_status(id:int, qpu_url)` checks if the circuit execution sent to `qpu_url` with `id` is finished. It returns the API response.

- `run_experiment(circuit, shots, qpu_url, polling_time = 10, max_requests = 1000)` performs the full pipeline to run an experiment
including:

   - Sending the task to the qcstack API at `qpu_url`.
   - Obtaining the experiment `id` and checking for solutions every `polling_time` secs for a maximum of `max_requests` times.
   - On success, return final JSON data.

- `get_bitstring_counts(response)` accepts the response of a successful experiment and returns a dictionary with the bitstring counts.
- `verify_ssl=False` is a Boolean module variable that enables or disables SSL verification when connecting to qcstack over HTTPS.
