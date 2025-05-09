import pytest

def test_QAOA():
    from qiskit_integration.qaoa_example import main
    _, bitstring, cut_value, _ = main()
    assert cut_value == 2
    assert bitstring in {"001", "110", "011", "100", "010", "101"}

def test_VQE(): 
    from qiskit_integration.vqe_example import main 
    result = main() 
    assert result.total_energies[0] == pytest.approx(-1.137306, abs=7.5e-3)