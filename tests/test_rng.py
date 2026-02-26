from app.rng.classical import get_classical_bytes
from app.rng.quantum import get_quantum_bytes
from app.rng.hybrid import get_random

def test_classical_rng_length():
    b = get_classical_bytes(32)
    assert isinstance(b, (bytes, bytearray))
    assert len(b) == 32

def test_quantum_rng_length():
    b = get_quantum_bytes(16)
    assert isinstance(b, (bytes, bytearray))
    assert len(b) == 16

def test_hybrid_modes_work():
    for mode in ["classical", "quantum", "hybrid_mix", "hybrid_failover"]:
        r = get_random(16, mode=mode)
        assert "random_hex" in r
        assert len(bytes.fromhex(r["random_hex"])) == 16
        assert 0 <= r["health_score"] <= 100
        assert "source" in r
