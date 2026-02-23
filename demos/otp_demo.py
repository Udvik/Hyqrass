import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def generate_otp():
    r = requests.get(f"{BASE_URL}/get_random", params={"n_bytes": 16, "mode": "hybrid_mix"}).json()
    num = int(r["random_number"], 16) % 1000000
    otp = f"{num:06d}"
    return otp, r

def main():
    otp, meta = generate_otp()
    expires_in = 30 
    expiry = time.time() + expires_in

    print("OTP:", otp)
    print("Source:", meta["source"], "Health:", meta["health_score"], "Latency(ms):", meta["latency_ms"])
    print(f"Valid for {expires_in} seconds...")

    user = input("Enter OTP: ").strip()
    if time.time() > expiry:
        print("❌ OTP expired")
    elif user == otp:
        print("✅ OTP verified")
    else:
        print("❌ Invalid OTP")

if __name__ == "__main__":
    main()
