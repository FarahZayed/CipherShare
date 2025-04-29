from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import os

backend = default_backend()
SALT = b'static_salt_here'  # Replace with random salt in production
ITERATIONS = 100_000
MARKER = b"CIPHERSHARE_OK"  # Known value to verify correct decryption

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

    with open(in_path, 'rb') as f_in, open(out_path, 'wb') as f_out:
        f_out.write(iv)  # Prepend IV
        f_out.write(encryptor.update(MARKER))  # Encrypt marker first

        while chunk := f_in.read(4096):
            f_out.write(encryptor.update(chunk))
        f_out.write(encryptor.finalize())

def decrypt_file(in_path, out_path, key):
    with open(in_path, 'rb') as f_in:
        iv = f_in.read(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        decryptor = cipher.decryptor()

        marker = decryptor.update(f_in.read(len(MARKER)))
        if marker != MARKER:
            raise ValueError("❌ Invalid password or corrupted file.")

        with open(out_path, 'wb') as f_out:
            while chunk := f_in.read(4096):
                f_out.write(decryptor.update(chunk))
            f_out.write(decryptor.finalize())
