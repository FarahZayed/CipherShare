from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import os
import hashlib

backend = default_backend()
SALT = b'static_salt_here'
ITERATIONS = 100_000
MARKER = b"CIPHERSHARE_OK"

def derive_key(password: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=ITERATIONS,
        backend=backend
    )
    return kdf.derive(password.encode())

def encrypt_file(in_path, out_path, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    encryptor = cipher.encryptor()

    with open(in_path, 'rb') as f_in:
        plaintext = f_in.read()

    # Compute SHA-256 hash of plaintext
    file_hash = hashlib.sha256(plaintext).digest()

    with open(out_path, 'wb') as f_out:
        f_out.write(iv)
        f_out.write(encryptor.update(MARKER))
        f_out.write(encryptor.update(file_hash))  # Encrypted hash
        f_out.write(encryptor.update(plaintext))
        f_out.write(encryptor.finalize())

def decrypt_file(in_path, out_path, key):
    with open(in_path, 'rb') as f_in:
        iv = f_in.read(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        decryptor = cipher.decryptor()

        marker = decryptor.update(f_in.read(len(MARKER)))
        if marker != MARKER:
            raise ValueError("❌ Invalid password or corrupted file.")

        stored_hash = decryptor.update(f_in.read(32))  # SHA-256 hash is 32 bytes

        decrypted_data = b""
        while chunk := f_in.read(4096):
            decrypted_data += decryptor.update(chunk)
        decrypted_data += decryptor.finalize()

        # Verify hash
        calculated_hash = hashlib.sha256(decrypted_data).digest()
        if stored_hash != calculated_hash:
            raise ValueError("❌ File integrity check failed! The file may be corrupted or altered.")

        with open(out_path, 'wb') as f_out:
            f_out.write(decrypted_data)
