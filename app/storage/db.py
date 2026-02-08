import sqlite3
import json
import time
from pathlib import Path

DB_PATH = Path("hyqraas.db")

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS rng_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            mode TEXT NOT NULL,
            source TEXT NOT NULL,
            n_bytes INTEGER NOT NULL,
            health_score INTEGER NOT NULL,
            metrics_json TEXT,
            latency_ms REAL NOT NULL
        )
        """)
        con.commit()

def log_request(mode: str, source: str, n_bytes: int, health_score: int, metrics: dict, latency_ms: float):
    init_db()
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO rng_logs (ts, mode, source, n_bytes, health_score, metrics_json, latency_ms) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (time.time(), mode, source, n_bytes, health_score, json.dumps(metrics), float(latency_ms))
        )
        con.commit()

def get_stats(last_n: int = 200):
    init_db()
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute("""
            SELECT source, COUNT(*), AVG(health_score), AVG(latency_ms)
            FROM (SELECT * FROM rng_logs ORDER BY id DESC LIMIT ?)
            GROUP BY source
        """, (last_n,))
        rows = cur.fetchall()
    return [
        {"source": r[0], "count": r[1], "avg_health": round(r[2], 2), "avg_latency_ms": round(r[3], 2)}
        for r in rows
    ]
