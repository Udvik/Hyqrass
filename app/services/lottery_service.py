from app.rng.hybrid import get_random

def pick_winner(participants: list):
    if not participants:
        raise ValueError("Participants list cannot be empty")

    r = get_random(n_bytes=16, mode="hybrid_mix")

    x = int(r["random_hex"], 16)
    idx = x % len(participants)

    winner = participants[idx]

    return {
        "participants": participants,
        "winner": winner,
        "meta": r
    }