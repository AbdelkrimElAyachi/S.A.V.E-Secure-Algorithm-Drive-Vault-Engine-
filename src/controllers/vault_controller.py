import os
import json
import random
from src.ui.login_window import LoginWindow
from src.ui.signin_window import SigninWindow
from src.ui.main_window import MainWindow
from src.ui.add_password_window import AddPasswordWindow
from src.crypto.mini_md5 import mini_md5
from src.crypto.mini_rsa import SimplifiedRSA
from src.crypto.mini_des import SimplifiedDES

# The S-DES session key is always stored as exactly 2 bytes
DES_KEY_BYTES = 2


class VaultController:
    def __init__(self):
        self.current_window = None
        self.vault_file_path = "vault.json"
        self.rsa = None          # RSA instance used for key-wrapping
        self.session_key = None  # 10-bit DES session key (int)

    # ------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------

    def start(self):
        """Show registration or login window depending on vault existence."""
        if not os.path.exists(self.vault_file_path):
            self.current_window = SigninWindow(controller=self)
        else:
            self.current_window = LoginWindow(controller=self)
        self.current_window.mainloop()

    # ------------------------------------------------------------------
    # Vault creation
    # ------------------------------------------------------------------

    def initialize_vault(self, master_password):
        """Called by SigninWindow when the user creates a new vault."""
        try:
            print(f"[Controller] Initializing vault with password: {master_password}")

            # 1. Hash the master password
            password_hash = mini_md5(master_password)
            print(f"[Crypto] Password hash: {password_hash}")

            # 2. Generate RSA key pair
            self.rsa = SimplifiedRSA()
            print(f"[Crypto] Generated RSA key pair (n={self.rsa.n})")

            # 3. Generate a random 10-bit DES session key
            self.session_key = random.randint(0, 1023)
            des_key_bytes = self.session_key.to_bytes(DES_KEY_BYTES, byteorder='big')
            print(f"[Crypto] Generated 10-bit DES key: {bin(self.session_key)}")

            # 4. Wrap the DES key with RSA
            encrypted_key_blocks = self.rsa.encrypt_key(des_key_bytes)
            encrypted_key_hex = [hex(block) for block in encrypted_key_blocks]
            print(f"[Crypto] Wrapped key with RSA: {encrypted_key_hex}")

            # 5. Build the vault structure
            vault_data = {
                "password_hash": password_hash,
                "rsa_public_key":  {"e": self.rsa.e, "n": self.rsa.n},
                "rsa_private_key": {"d": self.rsa.d, "n": self.rsa.n},
                "encrypted_des_key": encrypted_key_hex,
                "entries": []
            }

            # 6. Persist vault
            with open(self.vault_file_path, 'w') as f:
                json.dump(vault_data, f, indent=2)
            print(f"[Controller] Vault created at {self.vault_file_path}")

            # 7. Open main dashboard
            self.current_window.destroy()
            self.current_window = MainWindow(
                controller=self,
                session_key=bin(self.session_key)[2:]
            )
            self.current_window.mainloop()
            return True

        except Exception as e:
            print(f"[Error] Vault initialization failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def handle_login(self, master_password):
        """Called by LoginWindow when the user tries to unlock the vault."""
        try:
            print(f"[Controller] Verifying login password: {master_password}")

            # 1. Load vault
            with open(self.vault_file_path, 'r') as f:
                vault_data = json.load(f)
            print(f"[Controller] Vault loaded from {self.vault_file_path}")

            # 2. Verify password hash
            provided_hash = mini_md5(master_password)
            stored_hash   = vault_data["password_hash"]
            if provided_hash != stored_hash:
                print(f"[Error] Password hash mismatch!")
                print(f"[Error] Provided: {provided_hash}")
                print(f"[Error] Stored:   {stored_hash}")
                return False
            print(f"[Crypto] Password verified! Hash: {provided_hash}")

            # 3. Reconstruct the RSA instance from stored key material
            #    Use __new__ to skip __init__'s prime generation since we
            #    already have d, e, n from the vault.
            self.rsa   = SimplifiedRSA.__new__(SimplifiedRSA)
            self.rsa.n = vault_data["rsa_private_key"]["n"]
            self.rsa.d = vault_data["rsa_private_key"]["d"]
            self.rsa.e = vault_data["rsa_public_key"]["e"]

            # 4. Decrypt the wrapped DES key
            encrypted_blocks = [
                int(h, 16) for h in vault_data["encrypted_des_key"]
            ]
            print(f"[Crypto] Encrypted blocks: {encrypted_blocks}")

            decrypted_key_bytes = self.rsa.decrypt_key(
                encrypted_blocks, key_length=DES_KEY_BYTES
            )
            self.session_key = int.from_bytes(decrypted_key_bytes, byteorder='big')
            print(f"[Crypto] Unwrapped DES key: {bin(self.session_key)}")

            # 5. Open main dashboard
            self.current_window.destroy()
            self.current_window = MainWindow(
                controller=self,
                session_key=bin(self.session_key)[2:]
            )
            self.current_window.mainloop()
            return True

        except Exception as e:
            print(f"[Error] Login failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Lock
    # ------------------------------------------------------------------

    def handle_vault_lock(self):
        """Clear sensitive key material from memory and shut down."""
        print("[Controller] Clearing crypto keys from memory. Shutting down.")
        self.session_key = None
        self.rsa = None
        if self.current_window:
            self.current_window.destroy()

    # ------------------------------------------------------------------
    # Password entries
    # ------------------------------------------------------------------

    def open_add_password_modal(self):
        """Open the add-password dialog; refresh the display when it closes."""
        try:
            add_password_window = AddPasswordWindow(self.current_window, self)
            self.current_window.wait_window(add_password_window)
            self.refresh_vault_display()
        except Exception as e:
            print(f"[Error] Failed to open add password modal: {e}")

    def add_password_entry(self, entry):
        """
        Encrypt and save a new password entry.
        entry: dict with 'site', 'username', 'password' keys.
        Returns True on success, False otherwise.
        """
        try:
            print(f"[Controller] Adding password for: {entry['site']}")

            with open(self.vault_file_path, 'r') as f:
                vault_data = json.load(f)

            des = SimplifiedDES(self.session_key)

            encrypted_entry = {
                "site":     des.encrypt(self._pad_string(entry["site"])).hex(),
                "username": des.encrypt(self._pad_string(entry["username"])).hex(),
                "password": des.encrypt(self._pad_string(entry["password"])).hex(),
            }

            vault_data["entries"].append(encrypted_entry)

            with open(self.vault_file_path, 'w') as f:
                json.dump(vault_data, f, indent=2)

            print("[Crypto] Encrypted and saved password entry")
            return True

        except Exception as e:
            print(f"[Error] Failed to add password entry: {e}")
            return False

    def get_decrypted_entries(self):
        """
        Load and decrypt all password entries.
        Returns a list of dicts with 'site', 'username', 'password'.
        """
        try:
            with open(self.vault_file_path, 'r') as f:
                vault_data = json.load(f)

            des = SimplifiedDES(self.session_key)
            decrypted_entries = []

            for enc in vault_data.get("entries", []):
                try:
                    decrypted_entries.append({
                        "site":     des.decrypt(bytes.fromhex(enc["site"]))    .rstrip(b'\x00').decode('utf-8', errors='ignore'),
                        "username": des.decrypt(bytes.fromhex(enc["username"])).rstrip(b'\x00').decode('utf-8', errors='ignore'),
                        "password": des.decrypt(bytes.fromhex(enc["password"])).rstrip(b'\x00').decode('utf-8', errors='ignore'),
                    })
                except Exception as e:
                    print(f"[Warning] Failed to decrypt entry: {e}")

            return decrypted_entries

        except Exception as e:
            print(f"[Error] Failed to get decrypted entries: {e}")
            return []

    def refresh_vault_display(self):
        """Reload and redisplay all entries in the main window."""
        try:
            if isinstance(self.current_window, MainWindow):
                entries = self.get_decrypted_entries()
                self.current_window.refresh_records(entries)
                print(f"[Controller] Vault display refreshed with {len(entries)} entries")
        except Exception as e:
            print(f"[Error] Failed to refresh vault display: {e}")

    # ------------------------------------------------------------------
    # String padding helpers
    # ------------------------------------------------------------------

    def _pad_string(self, text, length=256):
        """Pad text with null bytes to a fixed length for consistent encryption."""
        if isinstance(text, str):
            text = text.encode('utf-8')
        return (text + b'\x00' * length)[:length]

    def _unpad_string(self, data):
        """Strip null-byte padding and return a clean string."""
        if isinstance(data, bytes):
            return data.rstrip(b'\x00').decode('utf-8', errors='ignore')
        return data.rstrip('\x00')