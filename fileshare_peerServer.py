import socket
import threading
import os
import json

from user_manager import register_user,login_user


SHARED_FOLDER = "shared"
os.makedirs(SHARED_FOLDER, exist_ok=True)


ACCESS_FILE = "file_access.json"
if not os.path.exists(ACCESS_FILE):
    with open(ACCESS_FILE, "w") as f:
        json.dump({}, f)

def load_access_control():
    with open(ACCESS_FILE, "r") as f:
        return json.load(f)

def save_access_control(data):
    with open(ACCESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


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
            
            if command.startswith("LIST|"):  
                username = command.split("|")[1].strip()
                access = load_access_control()
                
                files = [
                    f for f, meta in access.items()
                    if meta.get("owner") == username
                    or "ALL" in meta.get("shared_with", [])
                    or username in meta.get("shared_with", [])
                ]
                
                response = "\n".join(files)
                sock.send(response.encode())


            elif command.startswith("GET|"):
                parts = command.split("|")
                filename = parts[1]
                username = parts[2]
                access = load_access_control()
                filename = filename.replace(" ", "").strip()
                if filename not in access or username not in access[filename]["shared_with"] and "ALL" not in access[filename]["shared_with"]:
                    sock.send(b"FILE_NOT_FOUND")
                else:
                    filepath = os.path.join(SHARED_FOLDER, filename)
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as f:
                            sock.sendfile(f)
                        print(f"[>] Sent file '{filename}' to {username}")
                    else:
                        sock.send(b"FILE_NOT_FOUND")


            elif command.startswith("UPLOAD "):
                meta_parts = command[7:].split("|")  # filename|owner|user1,user2
                filename, owner, shared_raw = meta_parts[0], meta_parts[1], meta_parts[2]
                shared_with = [u.strip() for u in shared_raw.split(",")]
                filename = filename.replace(" ", "").strip()
                print(filename)
                filepath = os.path.join(SHARED_FOLDER, filename)
                with open(filepath, "wb") as f:
                    while True:
                        chunk = sock.recv(4096)
                        if not chunk:
                            break
                        f.write(chunk)

                # Update metadata
                access = load_access_control()
                access[filename] = {
                    "owner": owner,
                    "shared_with": shared_with
                }
                save_access_control(access)

                print(f"[<] Received '{filename}' shared with {shared_with}")

            
            elif command == "REGISTER":
                sock.send(b"USERNAME:")
                username = sock.recv(1024).decode().strip()

                sock.send(b"PASSWORD:")
                password = sock.recv(1024).decode().strip()

                success, message = register_user(username, password)
                sock.send(message.encode())

            elif command == "LOGIN":
                sock.send(b"USERNAME:")
                username = sock.recv(1024).decode().strip()

                sock.send(b"PASSWORD:")
                password = sock.recv(1024).decode().strip()

                success, message = login_user(username, password)
                sock.send(message.encode())

            elif command.startswith("MYFILES"):
                username = command.split(" ", 1)[1].strip()
                
                if os.path.exists(ACCESS_FILE):
                    with open(ACCESS_FILE, "r") as f:
                        access_data = json.load(f)
                    
                    files = [filename for filename, meta in access_data.items()
                            if meta.get("owner") == username]
                    
                    response = "\n".join(files) if files else "No files shared by you."
                    sock.send(response.encode())
                else:
                    sock.send(b"No access data available.")
            
            elif command.startswith("SEARCH"):
                try:
                    parts = command.split(" ", 2)
                    username = parts[1].strip()
                    keyword = parts[2].strip().lower()

                    if os.path.exists(ACCESS_FILE):
                        with open(ACCESS_FILE, "r") as f:
                            access_data = json.load(f)

                        # Search for files that match the keyword and are accessible to the user
                        matching_files = [
                            filename for filename, meta in access_data.items()
                            if keyword in filename.lower() and (
                                username in meta.get("shared_with", []) or
                                "ALL" in meta.get("shared_with", []) or
                                meta.get("owner") == username
                            )
                        ]

                        response = "\n".join(matching_files) if matching_files else "No matching files found."
                        sock.send(response.encode())
                    else:
                        sock.send(b"No access data available.")
                except Exception as e:
                    sock.send(f"[!] Error processing search: {e}".encode())
        
            elif command.startswith("UNSHARE"):
                try:
                    parts = command.split(" ", 3)
                    owner = parts[1].strip()
                    filename = parts[2].strip()
                    target_user = parts[3].strip()
                    filename = filename.replace(" ", "").strip()
                    if os.path.exists(ACCESS_FILE):
                        with open(ACCESS_FILE, "r") as f:
                            access_data = json.load(f)
                        print(filename in access_data)
                        print(access_data[filename].get("owner"))
                        if filename in access_data and access_data[filename].get("owner") == owner:
                            shared_list = access_data[filename].get("shared_with", [])

                            if target_user == "ALL":
                                access_data[filename]["shared_with"] = []
                                msg = f"[✓] All sharing removed from '{filename}'."
                            elif target_user in shared_list:
                                shared_list.remove(target_user)
                                access_data[filename]["shared_with"] = shared_list
                                msg = f"[✓] '{filename}' is no longer shared with {target_user}."
                            else:
                                msg = f"[!] File not shared with {target_user}."

                            with open(ACCESS_FILE, "w") as f:
                                json.dump(access_data, f, indent=4)

                            sock.send(msg.encode())
                        else:
                            sock.send(b"[!] You are not the owner or file does not exist.")
                    else:
                        sock.send(b"[!] Access control file missing.")
                except Exception as e:
                    sock.send(f"[!] Error during unshare(the file does not exist): {e}".encode())




        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            sock.close()

if __name__ == "__main__":
    port = int(input("Enter port to run peer server on: "))
    server = FileSharePeer(port)
    server.start_peer()
