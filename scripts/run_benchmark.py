
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
            timeout=100,
        )
        if (i + 1) % 100 == 0:
            print(f"{mode}: {i+1}/{count}")
        time.sleep(0.005)

def main():
    
    N_BYTES = 64
    N = 1000

    hit("classical", N, N_BYTES)
    hit("quantum", N, N_BYTES)
    hit("hybrid_mix", N, N_BYTES)

    print("Benchmark completed.")

if __name__ == "__main__":
    main()