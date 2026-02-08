from .online_tests import bytes_to_bits, monobit_fraction, runs_count, shannon_entropy_bits

def score_bytes(data: bytes) -> dict:
    bits = bytes_to_bits(data)
    p1 = monobit_fraction(bits)
    runs = runs_count(bits)
    ent = shannon_entropy_bits(bits)

    # Simple scoring rules (easy to explain in viva)
    score = 100

    # Monobit: penalize distance from 0.5
    score -= int(abs(p1 - 0.5) * 400)   # 0.05 off => -20

    # Runs: for n bits, expected runs roughly ~ n/2 for random bits (very rough)
    n = len(bits)
    expected = n / 2
    # penalize if runs too low or too high
    score -= int(min(abs(runs - expected) / expected, 1.0) * 30)

    # Entropy: max is 1.0
    score -= int((1.0 - ent) * 50)

    # clamp
    score = max(0, min(100, score))

    return {
        "health_score": score,
        "metrics": {
            "p_one": p1,
            "runs": runs,
            "entropy_per_bit": ent,
            "n_bits": n
        }
    }
