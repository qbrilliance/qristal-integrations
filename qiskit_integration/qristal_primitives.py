import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.qasm2 import dumps
from qiskit.primitives import BaseEstimatorV1, BaseSamplerV1, PrimitiveJob, EstimatorResult, SamplerResult
from qiskit.quantum_info import SparsePauliOp
import numpy as np
from typing import Union, Optional, List
import warnings

#Warn user if running a different qiskit version
required_qiskit_version = "1.2.0"
if qiskit.__version__ != required_qiskit_version:
    warnings.warn(f"Expected qiskit version 1.2.0 but running {qiskit.__version__}!")

class QristalSampler(BaseSamplerV1):
    """
    A custom implementation of a quantum circuit sampler based on qiskit's BaseSamplerV1 
    for arbitrary Qristal backends. 
    """

    def __init__(self, qristal_session):
        """
        Initialize the QristalSampler from an arbitrary Qristal session.

        Parameters
        ----------
        qristal_session : qristal.core.session 
            An instance of a Qristal session object.
        """
        super().__init__()
        self.qristal_session = qristal_session

    def _run(self, circuits, parameter_values=None, **kwargs):
        """
        Execute and collect samples from a batch of quantum circuits using the Qristal session.

        Parameters
        ----------
        circuits : list[qiskit.QuantumCircuit]
            A list of Qiskit QuantumCircuit objects.
        parameter_values : list[list[float]], optional
            Parameter bindings for each circuit, if applicable.
        **kwargs : dict
            Additional keyword arguments (currently unused).

        Returns
        -------
        PrimitiveJob
            A job object wrapping the execution and returning a SamplerResult upon completion.
        """
        def _job_fn():
            prob_dists = []
            metadata = []

            for i, circuit in enumerate(circuits):
                # Handle parameters
                if parameter_values:
                    values = parameter_values[i]
                    bound_circuit = circuit.assign_parameters(values)
                else:
                    bound_circuit = circuit
                #optional transpile circuit to QB native gate set
                bound_circuit = transpile(bound_circuit, basis_gates=['rx', 'ry', 'cz'], optimization_level=3)

                # Convert to QASM2
                qasm = dumps(bound_circuit)
                counts = self._send_to_backend(qasm)

                # Convert counts to probability distribution
                total = counts.total_counts()
                probs = {}
                for bitvec in counts:
                    bit_value = 0
                    for bit in reversed(bitvec):
                        bit_value = (bit_value << 1) | int(bit)  
                    probs[bit_value] = counts[bitvec] / total
                prob_dists.append(probs)
                metadata.append({"shots": total})

            return SamplerResult(prob_dists, metadata)

        job = PrimitiveJob(_job_fn)
        job._submit()
        return job

    def _send_to_backend(self, qasm_str: str) -> dict:
        """
        Send a OpenQASM2-formatted circuit to the Qristal backend and retrieve results.

        Parameters
        ----------
        qasm_str : str
            An OpenQASM2 representation of a quantum circuit.

        Returns
        -------
        qristal.core.MapVectorBoolInt
            A dictionary of measured bitstring counts as returned by qristal.core.session.results.
        """
        self.qristal_session.instring = qasm_str
        self.qristal_session.run()
        return self.qristal_session.results[0][0]

class QristalEstimator(BaseEstimatorV1):
    """
    A custom implementation of a quantum circuit estimator based on qiskit's BaseEstimatorV1 
    for arbitrary Qristal backends.
    """

    def __init__(self, qristal_sampler):
        """
        Initialize the QristalEstimator from an arbitrary QristalSampler.

        Parameters
        ----------
        qristal_sampler : QristalSampler 
            An instance of a QristalSampler object.
        """
        super().__init__()
        self.qristal_sampler = qristal_sampler

    def _run(
        self,
        circuits: List[QuantumCircuit],
        observables: List[Union[SparsePauliOp, str]],
        parameter_values: Optional[List[List[float]]] = None,
        **kwargs
    ) -> PrimitiveJob:
        """
        Evaluate expectation values of observables over a batch of parameterized circuits.

        Parameters
        ----------
        circuits : list[qiskit.QuantumCircuit]
            Quantum circuits to be executed.
        observables : list[qiskit.quantum_info.SparsePauliOp] or list[str]
            Observables for which to evaluate expectation values. Strings will be converted
            to Pauli operators with prefactors 1.0.
        parameter_values : list[list[float]], optional
            Parameter bindings for each circuit, if applicable.
        **kwargs : dict
            Additional keyword arguments (currently unused).

        Returns
        -------
        PrimitiveJob
            A job that will return an EstimatorResult containing the evaluated expectation values.
        """
        results = []

        for i in range(len(circuits)):
            circuit = circuits[i]
            observable = observables[i]

            # Bind parameters if needed
            if parameter_values:
                circuit = circuit.assign_parameters(parameter_values[i])

            # Convert string observable to SparsePauliOp
            if isinstance(observable, str):
                observable = SparsePauliOp.from_list([(observable, 1.0)])

            # Evaluate expectation value
            expectation = 0.0
            for pauli, coeff in zip(observable.paulis, observable.coeffs):
                meas_circuit = self._prepare_measurement_circuit(circuit, pauli)
                #optional: transpile circuit 
                meas_circuit = transpile(meas_circuit, basis_gates=['rx', 'ry', 'cz'], optimization_level=3)
                qasm_str = dumps(meas_circuit)
                counts = self.qristal_sampler._send_to_backend(qasm_str)
                exp_val = self._compute_expectation(counts, pauli)
                expectation += coeff * exp_val

            results.append(expectation.real)

        def _run_job():
            return EstimatorResult(
                values=np.array(results), 
                metadata=[{"shots": self.qristal_sampler.qristal_session.sn[0][0]}] * len(results)
            )
        job = PrimitiveJob(_run_job)
        job._submit()
        return job

    def _prepare_measurement_circuit(self, circuit: QuantumCircuit, pauli: SparsePauliOp) -> QuantumCircuit:
        """
        Prepare a circuit for measuring in the eigenbasis of the given Pauli operator.

        Parameters
        ----------
        circuit : qiskit.QuantumCircuit
            The base quantum circuit.
        pauli : qiskit.quantum_info.SparsePauliOp
            The Pauli operator to measure against.

        Returns
        -------
        qiskit.QuantumCircuit
            A modified circuit with basis-change gates and measurements added.
        """
        # Clone the circuit
        meas_circuit = circuit.copy()

        # Apply basis change gates based on Pauli terms
        for idx, pauli_char in enumerate(pauli.to_label()):
            if pauli_char == 'X':
                meas_circuit.ry(-1.0*np.pi/2.0, idx)
            elif pauli_char == 'Y':
                meas_circuit.rx(np.pi/2.0, idx)
            # 'Z' and 'I' require no change

        # Add measurements
        meas_circuit.measure_all()
        return meas_circuit

    def _compute_expectation(self, counts, pauli: SparsePauliOp) -> float:
        """
        Compute the expectation value of a Pauli observable from measurement results.

        Parameters
        ----------
        counts : qristal.core.MapVectorBoolInt
            A dictionary mapping measured bitstrings to counts as returned by qristal.core.session.results.
        pauli : qiskit.quantum_info.SparsePauliOp
            The Pauli observable for which to compute the expectation value.

        Returns
        -------
        float
            The computed expectation value.
        """
        # Compute expectation value from counts
        total_shots = counts.total_counts()
        expectation = 0.0
        for bitvec in counts:
            parity = 1
            for idx, bit in enumerate(reversed(bitvec)):
                if pauli.to_label()[idx] in ['X', 'Y', 'Z'] and bit == 1:
                    parity *= -1
            expectation += parity * counts[bitvec] / total_shots
        return expectation