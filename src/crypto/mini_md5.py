"""
Simplified MD5-like Hash Implementation
A lightweight hash function for password verification in S.A.V.E
Based on MD5 concepts but simplified for educational purposes
"""

import struct

class SimplifiedMD5:
    """
    A simplified MD5 implementation with:
    - 128-bit output (16 bytes)
    - 4 rounds of processing
    - 64-step constant table
    """
    
    # MD5 constants (sine table)
    K = [
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
        0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
        0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
        0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
        0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
        0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
        0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
        0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
        0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
    ]
    
    # Shift amounts for each round
    S = [
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
        5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
        4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
        6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
    ]
    
    # Message schedule indices
    G_INDICES = [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
        1, 6, 11, 0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12,
        5, 8, 11, 14, 1, 4, 7, 10, 13, 0, 3, 6, 9, 12, 15, 2,
        0, 7, 14, 5, 12, 3, 10, 1, 8, 15, 6, 13, 4, 11, 2, 9,
    ]
    
    def __init__(self):
        """Initialize MD5 state"""
        self.reset()
    
    def reset(self):
        """Reset to initial state"""
        self.a0 = 0x67452301
        self.b0 = 0xefcdab89
        self.c0 = 0x98badcfe
        self.d0 = 0x10325476
    
    @staticmethod
    def _leftrotate(value, amount):
        """Rotate left"""
        value &= 0xffffffff
        return ((value << amount) | (value >> (32 - amount))) & 0xffffffff
    
    def _ff(self, a, b, c, d, m, s, t):
        """Round 1 function"""
        f = (b & c) | (~b & d)
        a = (a + f + t + m) & 0xffffffff
        a = self._leftrotate(a, s)
        a = (a + b) & 0xffffffff
        return a
    
    def _gg(self, a, b, c, d, m, s, t):
        """Round 2 function"""
        f = (d & b) | (~d & c)
        a = (a + f + t + m) & 0xffffffff
        a = self._leftrotate(a, s)
        a = (a + b) & 0xffffffff
        return a
    
    def _hh(self, a, b, c, d, m, s, t):
        """Round 3 function"""
        f = b ^ c ^ d
        a = (a + f + t + m) & 0xffffffff
        a = self._leftrotate(a, s)
        a = (a + b) & 0xffffffff
        return a
    
    def _ii(self, a, b, c, d, m, s, t):
        """Round 4 function"""
        f = c ^ (b | ~d)
        a = (a + f + t + m) & 0xffffffff
        a = self._leftrotate(a, s)
        a = (a + b) & 0xffffffff
        return a
    
    def update(self, data):
        """Update hash with new data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Pre-processing: adding padding
        msg_len = len(data)
        msg = bytearray(data)
        
        # Append the '1' bit (plus zero padding to next byte boundary)
        msg.append(0x80)
        
        # Append zero padding
        while (len(msg) % 64) != 56:
            msg.append(0x00)
        
        # Append original length in bits as 64-bit little-endian
        msg += struct.pack('<Q', msg_len * 8)
        
        # Process message in 512-bit chunks
        for chunk_start in range(0, len(msg), 64):
            self._process_chunk(msg[chunk_start:chunk_start + 64])
    
    def _process_chunk(self, chunk):
        """Process a single 512-bit chunk"""
        # Break chunk into sixteen 32-bit little-endian words
        m = []
        for i in range(16):
            m.append(struct.unpack('<I', chunk[i*4:(i+1)*4])[0])
        
        # Initialize working variables
        a = self.a0
        b = self.b0
        c = self.c0
        d = self.d0
        
        # Main loop
        for i in range(64):
            if i < 16:
                f = (b & c) | (~b & d)
                g = i
                func = self._ff
            elif i < 32:
                f = (d & b) | (~d & c)
                g = (5 * i + 1) % 16
                func = self._gg
            elif i < 48:
                f = b ^ c ^ d
                g = (3 * i + 5) % 16
                func = self._hh
            else:
                f = c ^ (b | ~d)
                g = (7 * i) % 16
                func = self._ii
            
            a, b, c, d = d, func(a, b, c, d, m[self.G_INDICES[i]], self.S[i], self.K[i]), b, c
        
        # Add this chunk's hash to result so far
        self.a0 = (self.a0 + a) & 0xffffffff
        self.b0 = (self.b0 + b) & 0xffffffff
        self.c0 = (self.c0 + c) & 0xffffffff
        self.d0 = (self.d0 + d) & 0xffffffff
    
    def digest(self):
        """Return the digest as bytes"""
        return struct.pack('<4I', self.a0, self.b0, self.c0, self.d0)
    
    def hexdigest(self):
        """Return the digest as a hex string"""
        return self.digest().hex()


def mini_md5(data):
    """Convenience function to hash data and return hex digest"""
    hasher = SimplifiedMD5()
    hasher.update(data)
    return hasher.hexdigest()
