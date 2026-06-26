# S.A.V.E — Secure Algorithm Vault Engine

> A desktop password manager built from scratch using hand-crafted cryptographic algorithms — no third-party crypto libraries.

---

## Overview

**S.A.V.E** is a local password vault application with a graphical interface built using Python and `customtkinter`. every cryptographic primitive — hashing, symmetric encryption, and asymmetric key-wrapping — is implemented from the ground up as simplified, educational versions of real-world algorithms.
---

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/AbdelkrimElAyachi/S.A.V.E-Secure-Algorithm-Drive-Vault-Engine-.git
cd S.A.V.E-Secure-Algorithm-Drive-Vault-Engine-
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

> Dependencies: `customtkinter`, `darkdetect`, `packaging`

### Running the App

```bash
python -m src.app
```

On first launch, S.A.V.E will detect that no vault exists and present the **registration screen** to create a new vault with a master password. On subsequent launches, it will show the **login screen**.


---


## How It Works

S.A.V.E uses a **hybrid encryption architecture**:

```
Master Password
      │
      ▼
 [Mini MD5] ──────────────────────────► password_hash (stored in vault)
      
      │  (on vault creation)
      ▼
 [Mini RSA] ── generates key pair ────► public/private keys (stored in vault)

 [Random 10-bit key] ─► [Mini RSA encrypt] ──► encrypted_des_key (stored in vault)

      │  (on each credential save)
      ▼
 [Mini S-DES] ── encrypts entries ───► encrypted site / username / password
```

### Cryptographic Primitives

| Module | Algorithm | Purpose |
|---|---|---|
| `mini_md5.py` | Simplified MD5 (128-bit, 4-round) | Master password hashing & verification |
| `mini_rsa.py` | Simplified RSA (small primes) | Session key wrapping (asymmetric) |
| `mini_des.py` | Simplified S-DES (10-bit key, 2-round Feistel) | Symmetric encryption of stored credentials |

### Vault File Structure (`vault.json`)

```json
{
  "password_hash": "<mini-md5 hex digest of master password>",
  "rsa_public_key":  { "e": ..., "n": ... },
  "rsa_private_key": { "d": ..., "n": ... },
  "encrypted_des_key": ["0x..."],
  "entries": [
    {
      "site":     "<S-DES encrypted hex>",
      "username": "<S-DES encrypted hex>",
      "password": "<S-DES encrypted hex>"
    }
  ]
}
```

---

## Features

- 🔐 **Master password authentication** — vault unlocks only with the correct password, verified via a mini-MD5 hash
- 🔑 **RSA key-wrapping** — the symmetric session key is RSA-encrypted at rest; never stored in plaintext
- 🛡️ **S-DES encryption** — every credential field is encrypted byte-by-byte with a 10-bit Feistel cipher
- 🗂️ **Scrollable credential list** — view all stored sites and usernames at a glance
- 📋 **One-click copy** — copy any stored password to the clipboard instantly
- 🔒 **Lock vault** — clears all sensitive key material from memory on demand
- 💾 **Persistent local storage** — all data lives in a single `vault.json` file; nothing is sent over the network

---

## Project Structure

```
S.A.V.E/
├── src/
│   ├── app.py                         # Entry point
│   ├── controllers/
│   │   └── vault_controller.py        # Core application logic & crypto orchestration
│   ├── crypto/
│   │   ├── mini_md5.py                # Simplified MD5 hash implementation
│   │   ├── mini_rsa.py                # Simplified RSA implementation
│   │   └── mini_des.py                # Simplified S-DES (Feistel cipher) implementation
│   └── ui/
│       ├── login_window.py            # Login screen (existing vault)
│       ├── signin_window.py           # Registration screen (new vault)
│       ├── main_window.py             # Main dashboard (credential list)
│       └── add_password_window.py     # Add credential modal
├── requirements.txt
└── README.md
```

---


## Application Flow

```
First run          ──► Sign-in Window  ──► [Create vault + generate RSA keys + wrap DES key]
                                                        │
Subsequent runs    ──► Login Window ──► [Verify hash + unwrap DES key]
                                                        │
                                              Main Dashboard
                                         ┌─────────────────────┐
                                         │  + Add Password      │  ──► Add Password Modal
                                         │  Stored Credentials  │       (encrypt & save)
                                         │  Lock Vault          │  ──► Clear keys, exit
                                         └─────────────────────┘
```

---

## ⚠️ Disclaimer

The cryptographic implementations in this project (`mini_md5`, `mini_rsa`, `mini_des`) are **educational simplifications** of real-world algorithms. They are intentionally simplified (small key sizes, reduced rounds) and are **not suitable for production use**. This project is intended as a learning exercise in applied cryptography and GUI application design.
