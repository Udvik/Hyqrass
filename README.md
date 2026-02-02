# HyQRaaS — Hybrid Quantum Randomness-as-a-Service

HyQRaaS is a backend service that generates cryptographically secure random numbers by combining
**quantum randomness** (via Qiskit-based quantum circuits) with **classical OS entropy**.
Each generated output is validated in real time using lightweight statistical tests and is
returned along with a **health score** indicating randomness quality.

The system is designed to be **reliable, auditable, and fault-tolerant**, making it suitable
for security-critical applications such as authentication tokens, OTP generation, IoT security,
and fair selection systems.

---

## Key Features

- **Quantum Random Number Generation (QRNG)**
  - Hadamard-based quantum circuit with measurement
  - Implemented using Qiskit (simulator)

- **Classical Random Number Generation**
  - Cryptographically secure OS entropy (`os.urandom`)

- **Hybrid Randomness Modes**
  - Quantum only
  - Classical only
  - Hybrid mixing (quantum + classical with SHA-256 extraction)
  - Automatic failover if quantum quality is low or unavailable

- **Real-Time Validation**
  - Monobit test
  - Runs test
  - Shannon entropy estimation
  - Combined health score (0–100)

- **RNG-as-a-Service API**
  - Built with FastAPI
  - Returns randomness + quality metadata

- **Audit Logging**
  - SQLite logging of all requests
  - Aggregated statistics endpoint

---

## Technology Stack

- **Language:** Python 3.10+
- **Quantum Framework:** Qiskit, Qiskit Aer Simulator
- **Backend API:** FastAPI, Uvicorn
- **Validation:** NumPy, SciPy
- **Database:** SQLite
- **Hashing / Mixing:** SHA-256 (hashlib)

All tools and libraries used are **free and open-source**.

---


## Project Structure

