import socket
import threading
import os

SHARED_FOLDER = "shared"
os.makedirs(SHARED_FOLDER, exist_ok=True)

class FileSharePeer:
    def __init__(self, port):
        self.host = '127.0.0.1'
        self.port = port
        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_peer(self):
        self.peer_socket.bind((self.host, self.port))
        self.peer_socket.listen(5)
        print(f"[+] Peer server is listening on {self.port}...")

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

if __name__ == "__main__":
    port = int(input("Enter port to run peer server on: "))
    server = FileSharePeer(port)
    server.start_peer()
