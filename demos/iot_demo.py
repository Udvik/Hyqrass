import requests
import secrets

BASE_URL = "http://127.0.0.1:8000"
DEVICE_DB = {} 

def provision_device(device_id: str):
    r = requests.get(f"{BASE_URL}/get_random", params={"n_bytes": 32, "mode": "hybrid_mix"}).json()
    token = r["random_number"]
    DEVICE_DB[device_id] = token
    return device_id, token, r

def authenticate(device_id: str, token: str):
    expected = DEVICE_DB.get(device_id)
    return expected is not None and secrets.compare_digest(expected, token)

def main():
    device_id = "device-001"
    device_id, token, meta = provision_device(device_id)

    print("Provisioned:", device_id)
    print("Token:", token)
    print("Source:", meta["source"], "Health:", meta["health_score"])

    print("\nSimulate device request...")
    ok = authenticate(device_id, token)
    print("✅ Auth success" if ok else "❌ Auth failed")

    print("\nSimulate attacker request...")
    fake = "00" * 32
    ok2 = authenticate(device_id, fake)
    print("✅ Auth success (unexpected)" if ok2 else "❌ Auth failed (expected)")

if __name__ == "__main__":
    main()
