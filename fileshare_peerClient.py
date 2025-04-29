import socket
import os
from session_manager import get_current_user, is_logged_in,login_session,logout_session
from AESencry import encrypt_file, derive_key ,decrypt_file

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def list_files(peer_ip, peer_port):
    try:
        s = socket.socket()
        s.connect((peer_ip, peer_port))
        s.send(b"LIST")
        data = s.recv(4096).decode()
        print(f"\nFiles available:\n{data}")
        s.close()
    except Exception as e:
        print(f"[!] Error: {e}")



def download_file(peer_ip, peer_port, filename):
    try:
        password = input("Enter decryption password: ")
        key = derive_key(password)

        s = socket.socket()
        s.connect((peer_ip, peer_port))
        s.send(f"GET {filename}".encode())

        # First response
        first_chunk = s.recv(4096)
        if first_chunk == b"FILE_NOT_FOUND":
            print("[!] The requested file does not exist on the server.")
            s.close()
            return

        # Save encrypted file
        encrypted_path = os.path.join(DOWNLOAD_FOLDER, "temp_encrypted")
        with open(encrypted_path, "wb") as f:
            f.write(first_chunk)
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                f.write(chunk)
        s.close()

        decrypted_path = os.path.join(DOWNLOAD_FOLDER, filename)

        # ✅ Attempt decryption and handle failure
        try:
            decrypt_file(encrypted_path, decrypted_path, key)
            print(f"[✔] Decrypted and saved to '{decrypted_path}'")
        except ValueError as ve:
            print(f"[!] Decryption failed: {ve}")
            if os.path.exists(decrypted_path):
                os.remove(decrypted_path)  # delete invalid output
        finally:
            os.remove(encrypted_path)  # always remove temp encrypted

    except Exception as e:
        print(f"[!] Error downloading file: {e}")



def upload_file(peer_ip, peer_port, local_path):
    try:
        password = input("Enter encryption password: ")
        key = derive_key(password)

        temp_path = "temp_encrypted"  # use a fixed temp name

        encrypt_file(local_path, temp_path, key)

        filename = os.path.basename(local_path)  # send original filename
        s = socket.socket()
        s.connect((peer_ip, peer_port))
        s.send(f"UPLOAD {filename}".encode())

        with open(temp_path, "rb") as f:
            s.sendfile(f)

        s.close()
        os.remove(temp_path)
        print(f"[↑] Encrypted and uploaded '{filename}' to peer {peer_ip}:{peer_port}")
    except Exception as e:
        print(f"[!] Error uploading file: {e}")


def register_user(peer_ip, peer_port):
    try:
        s = socket.socket()
        s.connect((peer_ip, peer_port))
        s.send(b"REGISTER")

        prompt = s.recv(1024).decode()
        username = input(prompt)
        s.send(username.encode())

        prompt = s.recv(1024).decode()
        password = input(prompt)
        s.send(password.encode())

        result = s.recv(1024).decode()
        print(f"[REGISTER] {result}")
        s.close()
    except Exception as e:
        print(f"[!] Error during registration: {e}")

def login_user(peer_ip, peer_port):
    try:
        s = socket.socket()
        s.connect((peer_ip, peer_port))
        s.send(b"LOGIN")

        prompt = s.recv(1024).decode()
        username = input(prompt)
        s.send(username.encode())

        prompt = s.recv(1024).decode()
        password = input(prompt)
        s.send(password.encode())

        result = s.recv(1024).decode()
        print(f"[LOGIN] {result}")
        if "successful" in result:
             login_session(username)
        s.close()
    except Exception as e:
        print(f"[!] Error during login: {e}")

def logout_user():
    logout_session()


# --- Menu logic unchanged ---

def logged_in_menu():
    while True:
        print("\n--- Menu ---")
        print("1. List files on peer")
        print("2. Download file from peer")
        print("3. Upload file to peer")
        print("4. Logout")

        choice = input("Choose an option: ")

        if choice == "1":
            list_files(peer_ip, peer_port)
        elif choice == "2":
            fname = input("Enter filename to download: ")
            download_file(peer_ip, peer_port, fname)
        elif choice == "3":
            path = input("Enter full path to file to upload: ")
            if os.path.exists(path):
                upload_file(peer_ip, peer_port, path)
            else:
                print("[!] File not found.")
        elif choice == "4":
            print("Logging out...")
            logout_user()  
            
            break
        else:
            print("Invalid choice.")


def main_menu():
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ")
        
        if choice == "1":
            register_user(peer_ip, peer_port)
        elif choice == "2":
            login_user(peer_ip, peer_port)
            print("logging")
            print(is_logged_in())
            if is_logged_in():
                print(f"\n[LOGIN] Welcome, {get_current_user()}!")
                logged_in_menu()

        elif choice == "3":
            break
        else:
            print("Invalid choice.")

    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            register_user(peer_ip, peer_port)
        elif choice == "2":
           login_user(peer_ip, peer_port)
        elif choice == "3":
            break
        else:
            print("Invalid choice.")

        if is_logged_in():
            print(f"\nWelcome, {get_current_user()}!")
            
            
            print("\n--- Menu ---")
            print("1. List files on peer")
            print("2. Download file from peer")
            print("3. Upload file to peer")
            print("4. Exit")

            choice = input("Choose an option: ")

            if choice == "1":
                list_files(peer_ip, peer_port)
            elif choice == "2":
                fname = input("Enter filename to download: ")
                download_file(peer_ip, peer_port, fname)
            elif choice == "3":
                path = input("Enter full path to file to upload: ")
                if os.path.exists(path):
                    upload_file(peer_ip, peer_port, path)
                else:
                    print("[!] File not found.")
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice.")

                break

if __name__ == "__main__":
    peer_ip = input("Enter peer IP to connect to: ")
    peer_port = int(input("Enter peer port: "))

    main_menu()

       