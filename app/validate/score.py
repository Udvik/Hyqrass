# app/validate/score.py

from .online_tests import (
    bytes_to_bits,
    monobit_fraction,
    runs_count,
    shannon_entropy_bits,
    chi_square_test_bytes,
)

def score_bytes(data: bytes) -> dict:
    bits = bytes_to_bits(data)
    p1 = monobit_fraction(bits)
    runs = runs_count(bits)
    ent = shannon_entropy_bits(bits)
    chi = chi_square_test_bytes(data)

    n = len(bits)
    expected_runs = n / 2 if n > 0 else 0

    score = 100

    # Monobit penalty
    score -= int(abs(p1 - 0.5) * 400)

    # Runs penalty (penalize both too low and too high runs)
    if expected_runs > 0:
        run_dev = abs(runs - expected_runs) / expected_runs
        score -= int(min(run_dev, 1.0) * 60)

    # Chi-square penalty (lightweight)
    dof = chi.get("dof", 255)
    chi2 = chi.get("chi2", 0.0)
    if dof > 0:
        if chi2 > 2.0 * dof:
            score -= 10
        if chi2 > 3.0 * dof:
            score -= 20

    score = max(0, min(100, score))

    return {
        "health_score": score,
        "metrics": {
            "p_one": p1,
            "runs": runs,
            "entropy_per_bit": ent,
            "n_bits": n,
            "chi2": chi2,
            "chi2_dof": dof,
        },
    }