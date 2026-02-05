from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


_sim = AerSimulator()

def _bits_to_bytes(bitstring: str) -> bytes:
    
    
    if len(bitstring) % 8 != 0:
        pad = 8 - (len(bitstring) % 8)
        bitstring = bitstring + ("0" * pad)

    out = bytearray()
    for i in range(0, len(bitstring), 8):
        out.append(int(bitstring[i:i+8], 2))
    return bytes(out)

def get_quantum_bits(n_bits: int) -> str:
   
    if n_bits <= 0:
        raise ValueError("n_bits must be > 0")

    qc = QuantumCircuit(n_bits, n_bits)
    qc.h(range(n_bits))
    qc.measure(range(n_bits), range(n_bits))

    job = _sim.run(qc, shots=1)
    result = job.result()
    counts = result.get_counts()

    measured = next(iter(counts.keys())) 
    
    return measured[::-1]

def get_quantum_bytes(n_bytes: int) -> bytes:
   
    if n_bytes <= 0:
        raise ValueError("n_bytes must be > 0")

    bits = get_quantum_bits(n_bytes * 8)
    return _bits_to_bytes(bits)[:n_bytes]
