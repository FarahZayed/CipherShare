import os
import socket
from unittest.mock import patch
from fileshare_peerClient import (
    register_user, login_user, upload_file,
    list_files, download_file, logout_user, search_files, unshare_file, list_my_shared_files
)
from session_manager import login_session, get_current_user
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

peer_ip = "127.0.0.1"
peer_port = 9000
test_file = "testfile.txt"
#download_path = os.path.join("downloads", test_file)
download_path = os.path.join(DOWNLOAD_FOLDER, test_file)
# Create dummy file to upload
with open(test_file, "w") as f:
    f.write("Hello test!")

# Step 1: Register
with patch('builtins.input', side_effect=["testuser2", "password123"]):
    print("\n[TEST] Registering user...")
    register_user(peer_ip, peer_port)

# Step 2: Login
with patch('builtins.input', side_effect=["testuser2", "password123"]):
    print("\n[TEST] Logging in...")
    login_user(peer_ip, peer_port)

# Step 3: Upload File
with patch('builtins.input', side_effect=["password123", "ALL"]):
    print("\n[TEST] Uploading file...")
    upload_file(peer_ip, peer_port, test_file)

# Step 4: List Files
print("\n[TEST] Listing available files...")
list_files(peer_ip, peer_port)

# Step 5: Download File
with patch('builtins.input', side_effect=["password123"]):
    print("\n[TEST] Downloading file...")
    download_file(peer_ip, peer_port, test_file.strip().replace(" ",""))

# Step 7: Search for a keyword in files shared with the user
with patch('builtins.input', side_effect=[""]):
    print("\n[TEST] Searching for file using keyword 'test'...")
    search_files(peer_ip, peer_port, "test")

# Step 8: List the current user's files only
with patch('builtins.input', side_effect=[""]):
    print("\n[TEST] List the current user's files only '...")
    list_my_shared_files(peer_ip, peer_port)

# Step 9: Unshare the file from a specific user
with patch('builtins.input', side_effect=[test_file, "ALL"]):
    print(f"\n[TEST] Unsharing '{test_file}' from ALL users...")
    unshare_file(peer_ip, peer_port, test_file, "ALL")





# Step 10: Logout
print(f"\n[TEST] Logging Out...")
logout_user()

print("\n[✔] Test flow completed successfully.")
