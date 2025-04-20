
import secrets
from argon2 import PasswordHasher, exceptions

ph = PasswordHasher(
    time_cost=16,     # Number of iterations
    memory_cost=65536,  # 64 MB
    parallelism=2,
    hash_len=32,
    salt_len=16       # 128-bit salt
)

# Hash password
def hash_password(password):
    hashed = ph.hash(password)
    return hashed  

# Verify password
def verify_password(password, hashed_password):
    try:
        return ph.verify(hashed_password, password)
    except exceptions.VerifyMismatchError:
        return False

