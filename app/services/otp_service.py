import time
from app.rng.hybrid import get_random

def generate_otp(n_digits: int = 6):
    if n_digits <= 0 or n_digits > 12:
        raise ValueError("OTP length must be between 1 and 12")

    r = get_random(n_bytes=16, mode="hybrid_mix")

    num = int(r["random_hex"], 16) % (10 ** n_digits)
    otp = f"{num:0{n_digits}d}"

    expires_in = 30
    expiry_time = time.time() + expires_in

    return {
        "otp": otp,
        "n_digits": n_digits,
        "expires_in": expires_in,
        "expiry_time": expiry_time,
        "meta": r
    }