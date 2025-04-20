# import secrets
# from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
# from cryptography.hazmat.backends import default_backend
# from cryptography.exceptions import InvalidKey

# # Hash a password using Argon2id
# def hash_password(password, salt=None):
#     if salt is None:
#         salt = secrets.token_bytes(16)  # 128-bit salt

#     kdf = Argon2id(
#         salt=salt,
#         time_cost=16,
#         memory_cost=65536,  # in kibibytes (i.e., 64MB)
#         parallelism=2,
#         hash_len=32,
#         backend=default_backend()
#     )

#     hashed_password = kdf.derive(password.encode('utf-8'))
#     return hashed_password.hex(), salt.hex()

# # Verify password using Argon2id
# def verify_password(password, hashed_password_hex, salt_hex):
#     salt = bytes.fromhex(salt_hex)
#     hashed_password = bytes.fromhex(hashed_password_hex)

#     kdf = Argon2id(
#         salt=salt,
#         time_cost=16,
#         memory_cost=65536,
#         parallelism=2,
#         hash_len=32,
#         backend=default_backend()
#     )

#     try:
#         kdf.verify(password.encode('utf-8'), hashed_password)
#         return True
#     except InvalidKey:
#         return False



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
    print(hashed)
    return hashed  

# Verify password
def verify_password(password, hashed_password):
    try:
        return ph.verify(hashed_password, password)
    except exceptions.VerifyMismatchError:
        return False

