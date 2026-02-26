import math

def chi_square_test_bytes(data: bytes):
    """
    Chi-square test for uniformity over byte values (0..255).
    Returns (chi2, dof). Lower chi2 generally indicates closer to uniform.
    Note: This is a lightweight check, not a full NIST suite replacement.
    """
    if not data:
        return {"chi2": 0.0, "dof": 0}

    n = len(data)
    expected = n / 256.0

    # frequency of each byte value
    freq = [0] * 256
    for b in data:
        freq[b] += 1

    # chi-square statistic
    chi2 = 0.0
    for c in freq:
        diff = c - expected
        chi2 += (diff * diff) / expected if expected > 0 else 0.0

    dof = 255
    return {"chi2": chi2, "dof": dof}

def bytes_to_bits(data: bytes) -> str:
    return "".join(f"{b:08b}" for b in data)

def monobit_fraction(bits: str) -> float:
    ones = bits.count("1")
    return ones / len(bits)

def runs_count(bits: str) -> int:
    if not bits:
        return 0
    runs = 1
    for i in range(1, len(bits)):
        if bits[i] != bits[i-1]:
            runs += 1
    return runs

def shannon_entropy_bits(bits: str) -> float:
    if not bits:
        return 0.0
    p1 = bits.count("1") / len(bits)
    p0 = 1.0 - p1
    ent = 0.0
    for p in (p0, p1):
        if p > 0:
            ent -= p * math.log2(p)
    return ent
