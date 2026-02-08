from fastapi import FastAPI, Query
from app.rng.hybrid import get_random
from app.storage.db import log_request, get_stats

app = FastAPI(title="HyQRaaS", version="0.1")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/get_random")
def api_get_random(
    n_bytes: int = Query(16, ge=1, le=4096),
    mode: str = Query("hybrid_mix"),
    threshold: int = Query(60, ge=0, le=100),
    include_metrics: bool = Query(True),
):
    r = get_random(n_bytes=n_bytes, mode=mode, threshold=threshold)

    # ✅ SQLite log happens here
    log_request(
        mode=mode,
        source=r["source"],
        n_bytes=n_bytes,
        health_score=r["health_score"],
        metrics=r["metrics"],
        latency_ms=r["latency_ms"],
    )

    resp = {
        "random_number": r["random_hex"],
        "n_bytes": n_bytes,
        "source": r["source"],
        "health_score": r["health_score"],
        "latency_ms": r["latency_ms"],
    }
    if include_metrics:
        resp["metrics"] = r["metrics"]
    return resp

@app.get("/stats")
def stats(last_n: int = Query(200, ge=1, le=5000)):
    return {"last_n": last_n, "by_source": get_stats(last_n)}
