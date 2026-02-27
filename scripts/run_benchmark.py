# scripts/run_benchmark.py
import time
import requests

BASE = "http://127.0.0.1:8000"

def hit(mode: str, count: int, n_bytes: int):
    for i in range(count):
        requests.get(
            f"{BASE}/get_random",
            params={
                "n_bytes": n_bytes,
                "mode": mode,
                "include_metrics": True,
            },
            timeout=30,
        )
        if (i + 1) % 100 == 0:
            print(f"{mode}: {i+1}/{count}")
        time.sleep(0.005)

def main():
    # Use a fixed block size for fair comparison
    N_BYTES = 256
    N = 500  # set to 1000 for final run

    hit("classical", N, N_BYTES)
    hit("quantum", N, N_BYTES)
    hit("hybrid_mix", N, N_BYTES)

    print("Benchmark completed.")

if __name__ == "__main__":
    main()