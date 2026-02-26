import time
import requests

BASE = "http://127.0.0.1:8000"

def hit(mode: str, n_bytes=16, threshold=60, count=1000):
    for i in range(count):
        requests.get(f"{BASE}/get_random", params={
            "n_bytes": n_bytes,
            "mode": mode,
            "threshold": threshold,
            "include_metrics": True
        })
        if (i + 1) % 100 == 0:
            print(mode, i + 1)
        time.sleep(0.01)  # tiny delay so timestamps differ

def main():
    # Clean run: do each mode in blocks
    hit("classical", count=1000)
    hit("quantum", count=1000)
    hit("hybrid_mix", count=1000)
    hit("hybrid_failover", count=1000)  # optional

if __name__ == "__main__":
    main()