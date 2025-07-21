def main():
    import networkx as nx
    import qiskit_optimization
    import qiskit_algorithms
    from qiskit_optimization.applications import Maxcut
    from qiskit_optimization.converters import QuadraticProgramToQubo
    from qiskit.circuit.library import QAOAAnsatz
    from qiskit_algorithms import QAOA
    from qiskit_algorithms.optimizers import COBYLA
    from qiskit.result import QuasiDistribution
    import warnings

    import qristal.core
    from qiskit_integration.qristal_primitives import QristalSampler

    #Warn user if running a different qiskit versions
    required_qiskit_optimization_version = "0.6.1"
    if qiskit_optimization.__version__ != required_qiskit_optimization_version:
        warnings.warn(f"Expected qiskit-optimization version {required_qiskit_optimization_version} but running {qiskit_optimization.__version__}!")
    required_qiskit_algorithms_version = "0.3.1"
    if qiskit_algorithms.__version__ != required_qiskit_algorithms_version:
        warnings.warn(f"Expected qiskit-algorithms version {required_qiskit_algorithms_version} but running {qiskit_algorithms.__version__}!")


    # Step 1: Create MaxCut problem graph
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (1, 2), (0, 2)])
    print(graph)
    maxcut = Maxcut(graph)
    problem = maxcut.to_quadratic_program()

    # Step 2: Convert to QUBO
    qubo = QuadraticProgramToQubo().convert(problem)
    print("Mapped to QUBO optimization problem:")
    print(qubo)

    # Step 3: Convert QUBO to Ising Hamiltonian
    operator, offset = qubo.to_ising()

    # Step 4: Build qristal session and wrap in sampler
    sim = qristal.core.session()
    sim.acc = "aer"
    sim.qn = operator.num_qubits
    sim.sn = 1000
    sampler = QristalSampler(sim)

    # Step 4: Setup QAOA
    ansatz = QAOAAnsatz(operator, reps=1)
    optimizer = COBYLA(maxiter=200, tol=1e-4) 
    def print_callback(eval_count, parameters, mean, metadata):
        print(f"[{eval_count}] Cost: {mean:.8f}  Params: {parameters}")
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=1)
    qaoa.callback = print_callback

    # Step 5: Run QAOA
    result = qaoa.compute_minimum_eigenvalue(operator)

    # Step 7: Extract solution bitstring (as integer)
    distribution: QuasiDistribution = result.eigenstate  # quasi-probabilities
    most_likely_state = max(distribution.items(), key=lambda x: x[1])[0]  # int
    bitstring = format(most_likely_state, f"0{operator.num_qubits}b")  # binary string
    solution = [int(bit) for bit in bitstring]
    cut_edges = [(i, j) for i, j in graph.edges() if solution[i] != solution[j]]
    cut_value = len(cut_edges)  # or sum of weights if graph is weighted

    # Step 8: Display Results
    print("="*40)
    print("QAOA MaxCut Results")
    print(f"Optimal parameters: {result.optimal_point}")
    print(f"Estimated minimum cost: {result.eigenvalue.real + offset:.8f}")
    print(f"Most likely bitstring (solution): {bitstring}")
    print(f"Cut value: {cut_value}")
    print(f"Cut edges: {cut_edges}")
    print("="*40)

    return result, bitstring, cut_value, cut_edges

if __name__ == "__main__":
    main()