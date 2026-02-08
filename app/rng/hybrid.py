import hashlib
import time

from app.rng.classical import get_classical_bytes
from app.rng.quantum import get_quantum_bytes
from app.validate.score import score_bytes

DEFAULT_THRESHOLD = 60

def _expand_sha256(seed: bytes, n_bytes: int) -> bytes:
    """Expand a 32-byte seed into n_bytes using counter-based SHA-256."""
    out = b""
    counter = 0
    while len(out) < n_bytes:
        out += hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        counter += 1
    return out[:n_bytes]

def get_random(n_bytes: int, mode: str = "hybrid_mix", threshold: int = DEFAULT_THRESHOLD) -> dict:
    if n_bytes <= 0:
        raise ValueError("n_bytes must be > 0")

    t0 = time.time()
    source = mode

    if mode == "classical":
        raw = get_classical_bytes(n_bytes)
        source = "classical"

    elif mode == "quantum":
        raw = get_quantum_bytes(n_bytes)
        source = "quantum"

    elif mode == "hybrid_failover":
        # Try quantum first; fallback to classical on error/low score
        try:
            qraw = get_quantum_bytes(n_bytes)
            qscore = score_bytes(qraw)["health_score"]
            if qscore < threshold:
                raw = get_classical_bytes(n_bytes)
                source = "classical_fallback_low_score"
            else:
                raw = qraw
                source = "quantum"
        except Exception:
            raw = get_classical_bytes(n_bytes)
            source = "classical_fallback_error"

    elif mode == "hybrid_mix":
        # Mix quantum + classical, then extract with SHA-256
        qb = get_quantum_bytes(n_bytes)
        cb = get_classical_bytes(n_bytes)
        seed = hashlib.sha256(qb + cb).digest()
        raw = _expand_sha256(seed, n_bytes)
        source = "hybrid_mix"

    else:
        raise ValueError("mode must be one of: classical, quantum, hybrid_failover, hybrid_mix")

    scored = score_bytes(raw)
    latency_ms = (time.time() - t0) * 1000.0

    return {
        "bytes": raw,
        "random_hex": raw.hex(),
        "source": source,
        "health_score": scored["health_score"],
        "metrics": scored["metrics"],
        "latency_ms": round(latency_ms, 2),
    }
