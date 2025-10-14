import time
import uuid
import urllib3
import requests
from typing import Optional
from collections import Counter

class MyResult:
    def __init__(self, response: dict):
        self.response = response

    def get_counts(self) -> dict:
        """Convert bitstring array into Qiskit-style counts dictionary."""
        f = lambda x: "".join(map(str, x))
        bitstrings = list(map(f, self.response.get("data", [])))
        return dict(Counter(bitstrings))

    def __getitem__(self, key):
        return self.response[key]

    def __repr__(self):
        return f"MyResult({self.get_counts()})"


class MyJob:
    def __init__(self, circuit, shots, qpu_url, send_fn, poll_fn, polling_time=10, max_requests=100000):
        self.circuit = circuit
        self.shots = shots
        self.qpu_url = qpu_url
        self.send_experiment = send_fn
        self.get_experiment_status = poll_fn
        self.polling_time = polling_time
        self.max_requests = max_requests
        self._job_id = str(uuid.uuid4())
        self._result_cache = None

    def job_id(self):
        return self._job_id

    def status(self):
        return "COMPLETED" if self._result_cache else "RUNNING"

    def get_counts(self):
        """Shortcut: job.get_counts() instead of job.result().get_counts()."""
        return self.result().get_counts()

    def result(self):
        if self._result_cache:
            return MyResult(self._result_cache)  # wrap in MyResult

        print(f"Submitting experiment to: {self.qpu_url}")
        send_response = self.send_experiment(self.circuit, self.shots, self.qpu_url)
        if send_response.status_code != 200:
            raise RuntimeError("Failed to send experiment: " + str(send_response.json()))

        experiment_id = send_response.json().get("id")
        print(f"Experiment submitted. ID: {experiment_id}")

        for request_idx in range(1, self.max_requests + 1):
            response = self.get_experiment_status(experiment_id, self.qpu_url)

            if response.status_code == 200:
                print(f"Execution completed at request #{request_idx}")
                self._result_cache = response.json()
                return MyResult(self._result_cache)  # wrap here
            elif response.status_code == 425:
                print(f"Polling too early (#{request_idx}), waiting {self.polling_time}s...")
                time.sleep(self.polling_time)
            else:
                raise RuntimeError("Unexpected error from QPU: " + str(response.json()))

        raise TimeoutError("Polling timeout exceeded")

class QuantumBackend:
    """
    A class that wraps QB backend following Qiskit AerSimulator() structure.
    """

    def __init__(self, qpu_url: str, basis_gates=None, verify_ssl=False):
        
        if not qpu_url:
            raise ValueError("A valid qpu_url must be provided. Example: 'http://localhost:8888'")

        self.qpu_url = qpu_url
        self.verify_ssl = verify_ssl
        self.basis_gates = basis_gates or ['rx', 'ry', 'cz']
        
        # Check server status
        if not self._is_server_active():
            print(f"Cannot connect to QPU server at {self.qpu_url}. Is it running?")

        # Suppress SSL warnings globally
        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _is_server_active(self) -> bool:
        """Check if the QPU server is active and reachable."""
        try:
            response = requests.get(self.qpu_url, timeout=3, verify=self.verify_ssl)
            if response.status_code == 200:
                return True
            else:
                raise ConnectionError(
                    f"Server at {self.qpu_url} responded with status code {response.status_code}"
                )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise ConnectionError(
                f"Cannot connect to QPU server at {self.qpu_url}. Is it running?"
            )

    def transpile(self, circuit, basis_gates=None):
        try:
            from qiskit import transpile
            from qiskit.qasm2 import dumps  # QASM2 export
        except ImportError:
            raise ImportError("Qiskit is required but not installed.")

        # Use provided basis_gates or fall back to the default for this backend
        gates = basis_gates or self.basis_gates

        # Step 1: transpile using chosen basis gates
        circuit_transpiled = transpile(circuit, basis_gates=gates)

        # Step 2: check if only measurements remain in the circuit. If it does, re-transpile
        only_measurements = all(instr[0].name == "measure" for instr in circuit_transpiled.data)
        if only_measurements:
            circuit_transpiled = transpile(circuit, basis_gates=gates, optimization_level=0)

        # Step 3: return OpenQASM 2 string
        circuit_qasm = dumps(circuit_transpiled)
        return circuit_qasm

    # Check if circuit execution is finished and return response
    def get_experiment_status(self, id:int, qpu_url:str):
        url = qpu_url+"/api/v2/circuits/"+str(id)
        headers = {'accept': 'application/json'}
        response = requests.get(url, headers=headers, verify=self.verify_ssl)
        return response

    # Given circuit (string) array and shot count, send an experiment to qcstack API and return response
    def send_experiment(self, circuit, shots, qpu_url:str):
        headers = {'Content-Type': 'application/json'}
        json_data = {'circuit': circuit,'shots': shots}
        response = requests.post(qpu_url+"/api/v2/circuits/openqasm2", headers=headers, json=json_data, verify=self.verify_ssl)
        return response


    def run(self, circuit, shots: int,
            polling_time: int = 10, max_requests: int = 100000) -> Optional[dict]:
        
        # Set QPU server url
        qpu_url = self.qpu_url

        # Convert circuit to QASM 2 string if it's a Qiskit QuantumCircuit
        if hasattr(circuit, "draw"):
            circuit_qasm = self.transpile(circuit)
        elif isinstance(circuit, str):
            circuit_qasm = circuit
        else:
            raise ValueError("Invalid circuit type. Expected Qiskit circuit or QASM string.")

        # Convert circuit to list of lines
        circuit_lines = circuit_qasm.split("\n")
        
        # Return a job object (not the result directly!)
        return MyJob(
            circuit=circuit_lines,
            shots=shots,
            qpu_url=self.qpu_url,
            send_fn=self.send_experiment,
            poll_fn=self.get_experiment_status,
            polling_time=polling_time,
            max_requests=max_requests
        )

