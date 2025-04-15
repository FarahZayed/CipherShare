import socket
import threading
import os

SHARED_FOLDER = "shared"
os.makedirs(SHARED_FOLDER, exist_ok=True)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

class FileSharePeer:
    def __init__(self, port):
        self.host = '127.0.0.1'
        self.port = port
        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_peer(self):
        self.peer_socket.bind((self.host, self.port))
        self.peer_socket.listen(5)
        print(f"[+] Peer is listening on {self.port}...")

        while True:
            client_socket, addr = self.peer_socket.accept()
            print(f"[+] Connected with {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, sock):
        try:
            command = sock.recv(1024).decode()

            if command == "LIST":
                files = os.listdir(SHARED_FOLDER)
                response = "\n".join(files)
                sock.send(response.encode())

            elif command.startswith("GET "):
                filename = command[4:]
                filepath = os.path.join(SHARED_FOLDER, filename)
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        sock.sendfile(f)
                    print(f"[>] Sent file '{filename}'")
                else:
                    sock.send(b"FILE_NOT_FOUND")

            elif command.startswith("UPLOAD "):
                filename = command[7:]
                filepath = os.path.join(SHARED_FOLDER, filename)

                with open(filepath, "wb") as f:
                    while True:
                        chunk = sock.recv(4096)
                        if not chunk:
                            break
                        f.write(chunk)
                print(f"[<] Received and saved: {filename}")

        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            sock.close()

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

        print(f"[\u2714] Downloaded '{filename}' to '{filepath}'")
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
        print(f"[\u2191] Uploaded '{filename}' to peer {peer_ip}:{peer_port}")
    except Exception as e:
        print(f"[!] Error uploading file: {e}")

def discover_peers(rendezvous_ip, rendezvous_port):
    try:
        s = socket.socket()
        s.connect((rendezvous_ip, rendezvous_port))
        s.send(b"PEER")  # Request peer list
        peers = s.recv(4096).decode()
        print(f"[+] Peers discovered:\n{peers}")
        return peers.split("\n")
    except Exception as e:
        print(f"[!] Error discovering peers: {e}")
        return []

if __name__ == "__main__":
    port = int(input("Enter port to run peer on: "))
    threading.Thread(target=lambda: FileSharePeer(port).start_peer(), daemon=True).start()

    rendezvous_ip = input("Enter rendezvous server IP: ")
    rendezvous_port = int(input("Enter rendezvous server port: "))

    peers = discover_peers(rendezvous_ip, rendezvous_port)
    if peers:
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