"""
Simplified DES (S-DES) Implementation
A 10-bit key version of DES for educational purposes
Used for encrypting vault data in S.A.V.E
"""


class SimplifiedDES:
    """
    Simplified DES with:
    - 10-bit key
    - 8-bit plaintext/ciphertext blocks
    - 2 rounds
    """

    # S-boxes for substitution (simplified)
    S0 = [
        [1, 0, 3, 2],
        [3, 2, 1, 0],
        [0, 2, 1, 3],
        [3, 1, 3, 2]
    ]

    S1 = [
        [0, 1, 2, 3],
        [2, 0, 1, 3],
        [3, 0, 1, 2],
        [2, 1, 0, 3]
    ]

    # Permutation tables
    P10    = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]  # Key permutation
    P8     = [6, 3, 7, 4, 8, 5, 10, 9]         # Reduced key permutation
    IP     = [2, 7, 6, 3, 4, 8, 5, 1]          # Initial permutation
    IP_INV = [8, 1, 4, 5, 7, 3, 2, 6]          # True inverse of IP  (FIXED)
    EP     = [4, 1, 2, 3, 2, 3, 4, 1]          # Expansion permutation
    P4     = [2, 4, 3, 1]                       # 4-bit permutation

    def __init__(self, key):
        """Initialize with a 10-bit key (integer or binary string)."""
        if isinstance(key, str):
            self.key = int(key, 2) & 0x3FF
        else:
            self.key = int(key) & 0x3FF

        self.k1, self.k2 = self._generate_subkeys()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _permute(self, value, permutation, num_bits):
        """Apply a permutation table to a value."""
        result = 0
        for p in permutation:
            bit = (value >> (num_bits - p)) & 1
            result = (result << 1) | bit
        return result

    def _left_shift(self, value, positions, num_bits):
        """Circular left shift."""
        mask = (1 << num_bits) - 1
        return ((value << positions) | (value >> (num_bits - positions))) & mask

    def _generate_subkeys(self):
        """Generate two 8-bit subkeys from the 10-bit master key."""
        perm_key = self._permute(self.key, self.P10, 10)

        left  = (perm_key >> 5) & 0x1F
        right =  perm_key       & 0x1F

        # K1: shift each half left by 1
        left1  = self._left_shift(left,  1, 5)
        right1 = self._left_shift(right, 1, 5)
        k1 = self._permute((left1 << 5) | right1, self.P8, 10)

        # K2: shift each half left by 2 more (3 total from original)
        left2  = self._left_shift(left1,  2, 5)
        right2 = self._left_shift(right1, 2, 5)
        k2 = self._permute((left2 << 5) | right2, self.P8, 10)

        return k1, k2

    def _f_function(self, right4, subkey):
        """Feistel F function: expand, XOR with subkey, S-box, permute."""
        expanded = self._permute(right4, self.EP, 4)
        xored    = expanded ^ subkey

        left_half  = (xored >> 4) & 0x0F
        right_half =  xored       & 0x0F

        row0 = ((left_half  >> 3) & 1) * 2 + (left_half  & 1)
        col0 =  (left_half  >> 1) & 0x3
        row1 = ((right_half >> 3) & 1) * 2 + (right_half & 1)
        col1 =  (right_half >> 1) & 0x3

        s = (self.S0[row0][col0] << 2) | self.S1[row1][col1]
        return self._permute(s, self.P4, 4)

    def _encrypt_block(self, plaintext, key1, key2):
        """
        Encrypt a single 8-bit block with the standard S-DES Feistel structure:
            IP -> fK(k1) -> SW -> fK(k2) -> IP_INV
        """
        # Initial permutation
        p = self._permute(plaintext, self.IP, 8)
        L, R = (p >> 4) & 0x0F, p & 0x0F

        # Round 1
        L1 = L ^ self._f_function(R, key1)
        R1 = R

        # Switch (swap halves)
        L2, R2 = R1, L1

        # Round 2
        L3 = L2 ^ self._f_function(R2, key2)
        R3 = R2

        # Inverse initial permutation
        combined = (L3 << 4) | R3
        return self._permute(combined, self.IP_INV, 8)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encrypt(self, plaintext):
        """
        Encrypt plaintext (bytes or str).
        Returns ciphertext as bytes.
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')

        return bytes(
            self._encrypt_block(byte, self.k1, self.k2)
            for byte in plaintext
        )

    def decrypt(self, ciphertext):
        """
        Decrypt ciphertext (bytes or str).
        Returns plaintext as bytes.
        S-DES decryption is identical to encryption with subkeys reversed (k2, k1).
        """
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode('utf-8')

        return bytes(
            self._encrypt_block(byte, self.k2, self.k1)
            for byte in ciphertext
        )
