import requests

BASE_URL = "http://127.0.0.1:8000"

def pick_winner(participants):
    r = requests.get(f"{BASE_URL}/get_random", params={"n_bytes": 16, "mode": "hybrid_mix"}).json()
    x = int(r["random_number"], 16)
    idx = x % len(participants)
    return participants[idx], r

def main():
    participants = ["A", "B", "C", "D", "E", "F"]

    winner, meta = pick_winner(participants)
    print("Participants:", participants)
    print("Winner:", winner)
    print("Source:", meta["source"], "Health:", meta["health_score"], "Latency(ms):", meta["latency_ms"])

if __name__ == "__main__":
    main()
