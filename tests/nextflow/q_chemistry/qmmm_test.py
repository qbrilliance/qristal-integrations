# Nextflow integration with Qristal vqee
# CI tests for QMMM H20-H2 example
import pytest
from collections import deque

def tail(filename, n=10):
    with open(filename) as f:
        return deque(f, n)

def test_CI_230529_simple_qmmm():
    dt = tail('last.xyz', 1)[0].split()
    assert str(dt[0]) == 'H', "Failed test: CI_230529_simple_qmmm: H atom"
    assert float(dt[1]) == pytest.approx(2.585, abs=1e-3), "Failed test: CI_230529_simple_qmmm: H atom"
    assert float(dt[2]) == pytest.approx(2.000, abs=1e-3), "Failed test: CI_230529_simple_qmmm: H atom"
    assert float(dt[3]) == pytest.approx(2.000, abs=1e-3), "Failed test: CI_230529_simple_qmmm: H atom"

      