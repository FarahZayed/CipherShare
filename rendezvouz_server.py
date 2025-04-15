import socket
import threading

# Store active peers
active_peers = {}

def handle_client(client_socket):
    # Handle incoming client connection and register peer
    peer_address = client_socket.recv(1024).decode()
    active_peers[peer_address] = client_socket
    print(f"[+] Registered peer: {peer_address}")
    
    # Send list of active peers back to the client
    peer_list = "\n".join(active_peers.keys())
    client_socket.send(peer_list.encode())
    
    # Close the client connection
    client_socket.close()

def start_rendezvous_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[+] Rendezvous server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[+] Connection from {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 5000
    start_rendezvous_server(host, port)
