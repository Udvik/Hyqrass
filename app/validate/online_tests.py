import math

def bytes_to_bits(data: bytes) -> str:
    return "".join(f"{b:08b}" for b in data)

def monobit_fraction(bits: str) -> float:
    ones = bits.count("1")
    return ones / len(bits)

def runs_count(bits: str) -> int:
    # number of runs in bitstring
    if not bits:
        return 0
    runs = 1
    for i in range(1, len(bits)):
        if bits[i] != bits[i-1]:
            runs += 1
    return runs

def shannon_entropy_bits(bits: str) -> float:
    # entropy per bit (0..1)
    if not bits:
        return 0.0
    p1 = bits.count("1") / len(bits)
    p0 = 1.0 - p1
    ent = 0.0
    for p in (p0, p1):
        if p > 0:
            ent -= p * math.log2(p)
    # max for binary is 1
    return ent
