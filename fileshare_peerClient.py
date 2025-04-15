import socket
import os

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
        s = socket.socket()
        s.connect((peer_ip, peer_port))
        s.send(f"GET {filename}".encode())

        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                f.write(chunk)

        print(f"[✔] Downloaded '{filename}' to '{filepath}'")
        s.close()
    except Exception as e:
        print(f"[!] Error downloading file: {e}")

def upload_file(peer_ip, peer_port, local_path):
    try:
        filename = os.path.basename(local_path)
        s = socket.socket()
        s.connect((peer_ip, peer_port))
        s.send(f"UPLOAD {filename}".encode())

        with open(local_path, "rb") as f:
            s.sendfile(f)
        s.close()
        print(f"[↑] Uploaded '{filename}' to peer {peer_ip}:{peer_port}")
    except Exception as e:
        print(f"[!] Error uploading file: {e}")

if __name__ == "__main__":
    peer_ip = input("Enter peer IP to connect to: ")
    peer_port = int(input("Enter peer port: "))

    while True:
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
