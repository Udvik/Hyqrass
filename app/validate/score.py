from .online_tests import bytes_to_bits, monobit_fraction, runs_count, shannon_entropy_bits

def score_bytes(data: bytes) -> dict:
    bits = bytes_to_bits(data)
    p1 = monobit_fraction(bits)
    runs = runs_count(bits)
    ent = shannon_entropy_bits(bits)

   
    score = 100

    
    score -= int(abs(p1 - 0.5) * 400) 

    
    n = len(bits)
    expected = n / 2
    
    score -= int(min(abs(runs - expected) / expected, 1.0) * 30)

    
    score -= int((1.0 - ent) * 50)

    
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
