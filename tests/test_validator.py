from app.validate.score import score_bytes

def test_bad_patterns_score_low():
    zeros = score_bytes(b"\x00" * 16)["health_score"]
    ones  = score_bytes(b"\xff" * 16)["health_score"]
    aa    = score_bytes(bytes([0xAA]) * 16)["health_score"]

    # Bad patterns must be clearly worse than a decent random stream
    assert zeros < 40
    assert ones < 40
    assert aa < 60

def test_random_scores_reasonable():
    import os
    s = score_bytes(os.urandom(16))["health_score"]
    assert 0 <= s <= 100
