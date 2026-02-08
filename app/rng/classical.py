import os

def get_classical_bytes(n_bytes: int) -> bytes:
    
    if n_bytes <= 0:
        raise ValueError("n_bytes must be greater than 0")
    return os.urandom(n_bytes)
