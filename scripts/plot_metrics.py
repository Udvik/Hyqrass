import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "hyqraas.db"

def load_logs(limit=1000):
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"SELECT * FROM rng_logs ORDER BY id DESC LIMIT {int(limit)}",
        con
    )
    con.close()
    return df.sort_values("id")

def plot_health(df):
    plt.figure()
    plt.plot(df["id"], df["health_score"])
    plt.xlabel("Request ID")
    plt.ylabel("Health Score")
    plt.title("Health Score Over Time")
    plt.show()

def plot_latency_by_source(df):
    plt.figure()
    grouped = df.groupby("source")["latency_ms"].mean().sort_values()
    plt.bar(grouped.index, grouped.values)
    plt.xlabel("Source")
    plt.ylabel("Avg Latency (ms)")
    plt.title("Average Latency by Source")
    plt.xticks(rotation=25)
    plt.tight_layout()
    plt.show()

def main():
    df = load_logs(limit=1000)
    if df.empty:
        print("No logs found. Call /get_random a few times first.")
        return

    print(df.tail(5)[["id", "source", "health_score", "latency_ms"]])
    plot_health(df)
    plot_latency_by_source(df)

if __name__ == "__main__":
    main()
