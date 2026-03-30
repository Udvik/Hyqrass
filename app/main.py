from fastapi import FastAPI, Query
from app.rng.hybrid import get_random
from app.storage.db import log_request, get_stats
from app.services.otp_service import generate_otp
from app.services.lottery_service import pick_winner
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

app = FastAPI(title="HyQRaaS", version="0.1")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/get_random")
def api_get_random(
    n_bytes: int = Query(16, ge=1, le=4096),
    mode: str = Query("hybrid_mix"),
    threshold: int = Query(60, ge=0, le=100),
    include_metrics: bool = Query(True),
):
    r = get_random(n_bytes=n_bytes, mode=mode, threshold=threshold)

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

@app.get("/otp")
def api_generate_otp(n_digits: int = 6):
    result = generate_otp(n_digits)

    log_request(
        mode="otp",
        source=result["meta"]["source"],
        n_bytes=16,
        health_score=result["meta"]["health_score"],
        metrics=result["meta"]["metrics"],
        latency_ms=result["meta"]["latency_ms"],
    )

    return {
        "otp": result["otp"],
        "length": result["n_digits"],
        "expires_in": result["expires_in"],
        "source": result["meta"]["source"],
        "health_score": result["meta"]["health_score"],
        "latency_ms": result["meta"]["latency_ms"],
    }

@app.get("/otp-ui", response_class=HTMLResponse)
def otp_ui(request: Request):
    return templates.TemplateResponse("otp.html", {"request": request})


@app.get("/lottery-ui", response_class=HTMLResponse)
def lottery_ui(request: Request):
    return templates.TemplateResponse("lottery.html", {"request": request})


@app.post("/lottery")
def api_lottery(participants: List[str]):
    result = pick_winner(participants)

    return {
        "participants": result["participants"],
        "winner": result["winner"],
        "source": result["meta"]["source"],
        "health_score": result["meta"]["health_score"],
        "latency_ms": result["meta"]["latency_ms"],
    }

@app.get("/stats")
def stats(last_n: int = Query(200, ge=1, le=5000)):
    return {"last_n": last_n, "by_source": get_stats(last_n)}
