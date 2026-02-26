# scripts/compare_base_tests.py
#
# Base-paper style comparison + robustness metrics.
# Outputs:
# - Summary table (means + stability + tail metrics + failure rate)
# - PNG plots in results/
# - summary CSV in results/
#
# Usage:
#   python scripts/compare_base_tests.py

import json
import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


DB_PATH = Path("hyqraas.db")
RESULTS_DIR = Path("results")

# ---- Base-paper style thresholds (lightweight online subset) ----
MONOBIT_LOW = 0.45
MONOBIT_HIGH = 0.55
RUNS_TOL = 20
ENTROPY_MIN = 0.95

# ---- Robustness evaluation threshold ----
# Anything below this health score is considered "low-quality"
FAIL_THRESHOLD = 60


def _ensure_db_exists():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH.resolve()}\n"
            "Run the API and generate samples first so logs are created."
        )


def load_logs(limit: int = 5000) -> pd.DataFrame:
    _ensure_db_exists()
    con = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(
            """
            SELECT id, ts, mode, source, n_bytes, health_score, metrics_json, latency_ms
            FROM rng_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            con,
            params=(int(limit),),
        )
    finally:
        con.close()

    if df.empty:
        return df

    def parse_metrics(x):
        try:
            return json.loads(x) if x else {}
        except Exception:
            return {}

    metrics = df["metrics_json"].apply(parse_metrics)

    df["p_one"] = metrics.apply(lambda m: m.get("p_one"))
    df["runs"] = metrics.apply(lambda m: m.get("runs"))
    df["entropy_per_bit"] = metrics.apply(lambda m: m.get("entropy_per_bit"))
    df["n_bits"] = metrics.apply(lambda m: m.get("n_bits"))
    df["chi2"] = metrics.apply(lambda m: m.get("chi2"))
    df["chi2_dof"] = metrics.apply(lambda m: m.get("chi2_dof"))

    # Keep only rows where core metrics exist
    df = df.dropna(subset=["p_one", "runs", "entropy_per_bit", "n_bits"]).copy()

    # chronological order
    df = df.sort_values("id")
    return df


def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df["monobit_dev"] = (df["p_one"] - 0.5).abs()
    df["expected_runs"] = df["n_bits"] / 2.0
    df["runs_dev"] = (df["runs"] - df["expected_runs"]).abs()

    # Pass flags (base-paper style)
    df["pass_monobit"] = (df["p_one"] >= MONOBIT_LOW) & (df["p_one"] <= MONOBIT_HIGH)
    df["pass_runs"] = df["runs_dev"] <= RUNS_TOL
    df["pass_entropy"] = df["entropy_per_bit"] >= ENTROPY_MIN
    df["pass_all"] = df["pass_monobit"] & df["pass_runs"] & df["pass_entropy"]

    # Robustness failure flag (low-quality block)
    df["is_fail"] = df["health_score"] < FAIL_THRESHOLD

    return df


def summarize_by_source(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    g = df.groupby("source", dropna=False)

    summary = pd.DataFrame({
        "count": g.size(),
        "avg_monobit_dev": g["monobit_dev"].mean(),
        "avg_runs_dev": g["runs_dev"].mean(),
        "avg_entropy_per_bit": g["entropy_per_bit"].mean(),
        "pass_rate_%": g["pass_all"].mean() * 100.0,
        "avg_health_score": g["health_score"].mean(),
        "avg_latency_ms": g["latency_ms"].mean(),

        # ---- Stability (lower variance is better) ----
        "monobit_dev_std": g["monobit_dev"].std(),
        "runs_dev_std": g["runs_dev"].std(),
        "entropy_std": g["entropy_per_bit"].std(),

        # ---- Tail / worst-case behavior (higher is better) ----
        "health_p05": g["health_score"].quantile(0.05),
        "entropy_p05": g["entropy_per_bit"].quantile(0.05),

        # ---- Failure rate (lower is better) ----
        "fail_rate_%": g["is_fail"].mean() * 100.0,
    }).reset_index()

    # Round for display
    round_cols = [
        "avg_monobit_dev", "avg_runs_dev", "avg_entropy_per_bit",
        "pass_rate_%", "avg_health_score", "avg_latency_ms",
        "monobit_dev_std", "runs_dev_std", "entropy_std",
        "health_p05", "entropy_p05", "fail_rate_%"
    ]
    for c in round_cols:
        summary[c] = summary[c].astype(float).round(6 if "entropy" in c or "monobit" in c else 2)

    # Sort to highlight robustness:
    # 1) lower fail rate
    # 2) higher p05 health
    # 3) higher pass rate
    summary = summary.sort_values(
        by=["fail_rate_%", "health_p05", "pass_rate_%"],
        ascending=[True, False, False]
    ).reset_index(drop=True)

    return summary


def _save_bar(summary: pd.DataFrame, value_col: str, title: str, ylabel: str, filename: str):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure()
    plt.bar(summary["source"], summary[value_col])
    plt.title(title)
    plt.xlabel("Source")
    plt.ylabel(ylabel)
    plt.xticks(rotation=25)
    plt.tight_layout()
    out_path = RESULTS_DIR / filename
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def _save_boxplot(df: pd.DataFrame, y_col: str, title: str, ylabel: str, filename: str):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure()

    # Collect data per source in current source order (sorted by name for consistent plot)
    sources = sorted(df["source"].unique())
    data = [df.loc[df["source"] == s, y_col].dropna().values for s in sources]

    plt.boxplot(data, labels=sources, showfliers=True)
    plt.title(title)
    plt.xlabel("Source")
    plt.ylabel(ylabel)
    plt.xticks(rotation=25)
    plt.tight_layout()

    out_path = RESULTS_DIR / filename
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def main():
    print("Loading logs...")
    df = load_logs(limit=5000)
    if df.empty:
        print("No usable logs found. Generate logs (call /get_random with include_metrics=True) and retry.")
        return

    df = compute_metrics(df)

    print("\nExperiment thresholds used:")
    print(f"- Monobit pass: {MONOBIT_LOW} <= p_one <= {MONOBIT_HIGH}")
    print(f"- Runs pass: |runs - (n_bits/2)| <= {RUNS_TOL}")
    print(f"- Entropy pass: entropy_per_bit >= {ENTROPY_MIN}")
    print(f"- Failure (robustness): health_score < {FAIL_THRESHOLD}")

    summary = summarize_by_source(df)

    print("\nSummary by source (base tests + robustness metrics):")
    print(summary.to_string(index=False))

    # ---- Base-paper plots ----
    _save_bar(
        summary, "avg_monobit_dev",
        "Average Monobit Deviation by Source (lower is better)",
        "Avg |p_one - 0.5|",
        "monobit_deviation_by_source.png",
    )
    _save_bar(
        summary, "avg_runs_dev",
        "Average Runs Deviation by Source (lower is better)",
        "Avg |runs - expected_runs|",
        "runs_deviation_by_source.png",
    )
    _save_bar(
        summary, "avg_entropy_per_bit",
        "Average Entropy per Bit by Source (higher is better)",
        "Avg entropy_per_bit",
        "entropy_per_bit_by_source.png",
    )
    _save_bar(
        summary, "pass_rate_%",
        "Overall Pass Rate by Source (higher is better)",
        "Pass rate (%)",
        "pass_rate_by_source.png",
    )

    # ---- Robustness plots (where hybrid should shine, if it does) ----
    _save_bar(
        summary, "fail_rate_%",
        f"Failure Rate by Source (health_score < {FAIL_THRESHOLD}) (lower is better)",
        "Failure rate (%)",
        "failure_rate_by_source.png",
    )
    _save_bar(
        summary, "health_p05",
        "5th Percentile Health Score by Source (higher is better)",
        "Health score (p05)",
        "health_p05_by_source.png",
    )
    _save_bar(
        summary, "entropy_p05",
        "5th Percentile Entropy/bit by Source (higher is better)",
        "Entropy per bit (p05)",
        "entropy_p05_by_source.png",
    )

    # Boxplots
    _save_boxplot(
        df, "health_score",
        "Health Score Distribution by Source (boxplot)",
        "Health score",
        "health_score_boxplot.png",
    )
    _save_boxplot(
        df, "entropy_per_bit",
        "Entropy per Bit Distribution by Source (boxplot)",
        "Entropy per bit",
        "entropy_per_bit_boxplot.png",
    )

    # Save CSV summary for report/PPT
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS_DIR / "summary_by_source.csv"
    summary.to_csv(csv_path, index=False)
    print(f"Saved: {csv_path}")

    print("\nDone. Use the PNG files in results/ for your report/PPT.")


if __name__ == "__main__":
    main()