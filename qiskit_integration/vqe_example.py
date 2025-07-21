def main():
    import qiskit_nature
    import qiskit_algorithms
    from qiskit_nature.second_q.circuit.library import HartreeFock, UCCSD
    from qiskit_nature.second_q.mappers import JordanWignerMapper
    from qiskit_nature.second_q.drivers import PySCFDriver
    from qiskit_nature.second_q.algorithms import GroundStateEigensolver
    from qiskit_algorithms import VQE
    from qiskit_algorithms.optimizers import COBYLA
    import numpy as np
    import warnings

    import qristal.core
    from qiskit_integration.qristal_primitives import QristalSampler, QristalEstimator

    #Warn user if running a different qiskit versions
    required_qiskit_nature_version = "0.7.2"
    if qiskit_nature.__version__ != required_qiskit_nature_version:
        warnings.warn(f"Expected qiskit-nature version {required_qiskit_nature_version} but running {qiskit_nature.__version__}!")
    required_qiskit_algorithms_version = "0.3.1"
    if qiskit_algorithms.__version__ != required_qiskit_algorithms_version:
        warnings.warn(f"Expected qiskit-algorithms version {required_qiskit_algorithms_version} but running {qiskit_algorithms.__version__}!")

    # Step 1: Define the molecular problem
    driver = PySCFDriver(atom="H 0 0 0; H 0 0 0.735", basis="sto3g")
    es_problem = driver.run()

    # Step 2: Map to qubit operators
    mapper = JordanWignerMapper()

    # Step 3: Construct the ansatz
    ansatz = UCCSD(
        es_problem.num_spatial_orbitals,
        es_problem.num_particles,
        mapper,
        initial_state=HartreeFock(
            es_problem.num_spatial_orbitals,
            es_problem.num_particles,
            mapper,
        ),
    )

    # Step 4: Build qristal session and wrap in estimator
    sim = qristal.core.session()
    sim.acc = "aer"
    sim.qn = 4
    sim.sn = 10000
    estimator = QristalEstimator(QristalSampler(sim))

    # Step 5: Set up the VQE solver
    def print_callback(eval_count, parameters, mean, metadata):
        print(f"[{eval_count}] Energy: {mean:.8f}  Params: {parameters}")
    lower_bounds = [0.0] * ansatz.num_parameters
    upper_bounds = [2.0 * np.pi] * ansatz.num_parameters
    bounds = list(zip(lower_bounds, upper_bounds))
    optimizer = COBYLA(maxiter=200, tol=1e-4) 
    vqe_solver = VQE(estimator, ansatz, optimizer)
    vqe_solver.initial_point = [0.1] * ansatz.num_parameters
    vqe_solver.callback = print_callback

    # Step 6: Compute the ground state
    calc = GroundStateEigensolver(mapper, vqe_solver)
    result = calc.solve(es_problem)

    # Step 7: Display Results
    print("="*40)
    print("VQE Results")
    print(f"Electronic energy: {result.raw_result.eigenvalue.real:.8f}")
    print(f"Total energy: {result.total_energies[0]:.8f}")
    print("="*40)

    return result

if __name__ == "__main__":
    main()