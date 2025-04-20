import json
import os
from crypto_utils import hash_password, verify_password

USER_DB = "CipherShare/users.json"

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        print("save users")
        json.dump(users, f)

def register_user(username, password):
    users = load_users()
    print(users)
    if username in users:
        return False, "Username already exists."

    hashed = hash_password(password)
    users[username] = {"hashed": hashed}
    print("in register")
    # print(users.toString())
    save_users(users)
    return True, "Registration successful."

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "User not found."

    # salt = users[username]["salt"]
    hashed = users[username]["hashed"]

    if verify_password(password, hashed):
        return True, "Login successful."
    else:
        return False, "Incorrect password."
