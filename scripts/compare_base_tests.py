# scripts/compare_base_tests.py
#
# Minimal comparison script (faculty presentation version)
# Prints only essential base-paper metrics.

import json
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("hyqraas.db")

# Base-paper thresholds
MONOBIT_LOW = 0.45
MONOBIT_HIGH = 0.55
RUNS_TOL = 20
ENTROPY_MIN = 0.95


def load_logs():
    if not DB_PATH.exists():
        raise FileNotFoundError("hyqraas.db not found. Run benchmark first.")

    con = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(
            """
            SELECT source, health_score, metrics_json, latency_ms
            FROM rng_logs
            """,
            con,
        )
    finally:
        con.close()

    def parse_metrics(x):
        try:
            return json.loads(x) if x else {}
        except Exception:
            return {}

    m = df["metrics_json"].apply(parse_metrics)

    df["p_one"] = m.apply(lambda d: d.get("p_one"))
    df["runs"] = m.apply(lambda d: d.get("runs"))
    df["entropy_per_bit"] = m.apply(lambda d: d.get("entropy_per_bit"))
    df["n_bits"] = m.apply(lambda d: d.get("n_bits"))

    df = df.dropna(subset=["p_one", "runs", "entropy_per_bit", "n_bits"]).copy()
    return df


def compute(df):
    df["monobit_dev"] = (df["p_one"] - 0.5).abs()
    df["expected_runs"] = df["n_bits"] / 2.0
    df["runs_dev"] = (df["runs"] - df["expected_runs"]).abs()

    df["pass_monobit"] = (df["p_one"] >= MONOBIT_LOW) & (df["p_one"] <= MONOBIT_HIGH)
    df["pass_runs"] = df["runs_dev"] <= RUNS_TOL
    df["pass_entropy"] = df["entropy_per_bit"] >= ENTROPY_MIN
    df["pass_all"] = df["pass_monobit"] & df["pass_runs"] & df["pass_entropy"]

    return df


def summarize(df):
    g = df.groupby("source")

    summary = pd.DataFrame({
        "Monobit Deviation": g["monobit_dev"].mean(),
        "Runs Deviation": g["runs_dev"].mean(),
        "Entropy per Bit": g["entropy_per_bit"].mean(),
        "Pass Rate (%)": g["pass_all"].mean() * 100.0,
        "Avg Latency (ms)": g["latency_ms"].mean(),
    }).reset_index()

    # Round values for clean display
    summary["Monobit Deviation"] = summary["Monobit Deviation"].round(4)
    summary["Runs Deviation"] = summary["Runs Deviation"].round(2)
    summary["Entropy per Bit"] = summary["Entropy per Bit"].round(4)
    summary["Pass Rate (%)"] = summary["Pass Rate (%)"].round(2)
    summary["Avg Latency (ms)"] = summary["Avg Latency (ms)"].round(2)

    return summary


def main():
    df = load_logs()
    df = compute(df)
    summary = summarize(df)

    print("\nComparison\n")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()