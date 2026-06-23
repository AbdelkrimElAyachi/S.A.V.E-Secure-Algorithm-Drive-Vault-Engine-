"""
Simplified RSA Implementation
A lightweight RSA implementation for key wrapping in S.A.V.E
Used to encrypt/decrypt the symmetric encryption key
"""

import random
import math


class SimplifiedRSA:
    """
    Simplified RSA with:
    - Small prime numbers (practical key size)
    - Public/Private key pair generation
    - Encryption and decryption
    """

    # Small primes for testing (in production, use much larger primes)
    SMALL_PRIMES = [61, 53, 59, 67, 71, 73, 79, 83, 89, 97]

    def __init__(self, p=None, q=None):
        """
        Initialize RSA with primes p and q.
        If not provided, random distinct small primes are chosen.
        """
        if p is None or q is None:
            p = random.choice(self.SMALL_PRIMES)
            q = random.choice([prime for prime in self.SMALL_PRIMES if prime != p])

        self.p   = p
        self.q   = q
        self.n   = p * q
        self.phi = (p - 1) * (q - 1)
        self.e   = self._choose_e()
        self.d   = self._mod_inverse(self.e, self.phi)

    # ------------------------------------------------------------------
    # Key generation helpers
    # ------------------------------------------------------------------

    def _choose_e(self):
        """Choose public exponent e such that gcd(e, phi) == 1."""
        e = random.randint(2, self.phi - 1)
        while math.gcd(e, self.phi) != 1:
            e = random.randint(2, self.phi - 1)
        return e

    @staticmethod
    def _gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def _mod_inverse(a, m):
        """Modular inverse via extended Euclidean algorithm."""
        if SimplifiedRSA._gcd(a, m) != 1:
            raise ValueError("Modular inverse does not exist")

        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            return gcd, y1 - (b // a) * x1, x1

        _, x, _ = extended_gcd(a % m, m)
        return (x % m + m) % m

    @staticmethod
    def _power_mod(base, exp, mod):
        """Fast modular exponentiation."""
        result = 1
        base %= mod
        while exp > 0:
            if exp & 1:
                result = result * base % mod
            exp >>= 1
            base = base * base % mod
        return result

    # ------------------------------------------------------------------
    # Core encrypt / decrypt
    # ------------------------------------------------------------------

    def encrypt(self, plaintext):
        """
        Encrypt an integer (or bytes) with the public key (e, n).
        Returns an integer ciphertext.
        """
        if isinstance(plaintext, bytes):
            plaintext = int.from_bytes(plaintext, byteorder='big')
        elif isinstance(plaintext, str):
            plaintext = int(plaintext)

        if plaintext >= self.n:
            raise ValueError(f"Plaintext {plaintext} must be less than n={self.n}")

        return self._power_mod(plaintext, self.e, self.n)

    def decrypt(self, ciphertext):
        """
        Decrypt an integer ciphertext with the private key (d, n).
        Returns an integer plaintext.
        """
        if isinstance(ciphertext, bytes):
            ciphertext = int.from_bytes(ciphertext, byteorder='big')
        return self._power_mod(ciphertext, self.d, self.n)

    # ------------------------------------------------------------------
    # Key-wrapping helpers (used by VaultController)
    # ------------------------------------------------------------------

    def encrypt_key(self, key_bytes):
        """
        Wrap a symmetric key (bytes) with RSA.
        Returns a list of encrypted integer blocks.
        """
        key_int = int.from_bytes(key_bytes, byteorder='big')

        if key_int < self.n:
            return [self.encrypt(key_int)]

        # Break into chunks that each fit under n
        chunk_size = ((self.n.bit_length() - 1) + 7) // 8
        blocks = []
        for i in range(0, len(key_bytes), chunk_size):
            chunk = key_bytes[i:i + chunk_size]
            blocks.append(self.encrypt(int.from_bytes(chunk, byteorder='big')))
        return blocks

    def decrypt_key(self, encrypted_blocks, key_length=2):
        """
        Unwrap a symmetric key encrypted with RSA.

        key_length: expected byte length of the original key (default 2 for
                    the 10-bit S-DES key).  Passing this explicitly avoids
                    silent truncation when the decrypted integer has leading
                    zero bytes (e.g. a key value of 5 -> 0x0005).

        Returns bytes of exactly key_length bytes.
        """
        decrypted = [self.decrypt(block) for block in encrypted_blocks]

        if len(decrypted) == 1:
            # Single block: always restore to the declared key length so that
            # leading zero bytes are preserved (e.g. key=5 -> b'\x00\x05').
            return decrypted[0].to_bytes(key_length, byteorder='big')

        # Multi-block: reconstruct chunk by chunk then trim to key_length
        chunk_size = ((self.n.bit_length() - 1) + 7) // 8
        key_bytes = b''.join(d.to_bytes(chunk_size, byteorder='big') for d in decrypted)
        return key_bytes[-key_length:]   # keep the rightmost key_length bytes

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    def get_public_key(self):
        return (self.e, self.n)

    def get_private_key(self):
        return (self.d, self.n)


# ---------------------------------------------------------------------------
# Module-level utility functions
# ---------------------------------------------------------------------------

def generate_rsa_keypair(p=None, q=None):
    """Generate and return a new RSA key pair."""
    return SimplifiedRSA(p, q)


def rsa_encrypt(message, public_key):
    """Encrypt using a public-key tuple (e, n)."""
    e, n = public_key
    if isinstance(message, (str, bytes)):
        message = int.from_bytes(
            message.encode() if isinstance(message, str) else message,
            byteorder='big'
        )
    return pow(message, e, n)


def rsa_decrypt(ciphertext, private_key):
    """Decrypt using a private-key tuple (d, n)."""
    d, n = private_key
    return pow(ciphertext, d, n)
