import socket
import threading
import argparse
import os

banner = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠋⠀⠉⠢⢀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⡁⠀⠀⠀⠀⠀⠑⠠⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡏⠑⢄⡀⠀⠀⠀⠀⠈⠑⢄⡀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣇⣀⣰⢉⣦⣄⠀⠀⠀⠀⠀⠈⢢
⠀⠀⠀⠀⠀⠀⠀⠀⡠⠐⠊⠁⠀⢩⣿⣯⡶⠃⠢⡀⠀⠀⡠⠊
⠀⠀⠀⠀⠀⠀⡠⠊⠀⠀⠀⠀⢠⡟⠁⢹⠀⡀⠄⠚⠑⠒⠁⠀
⠀⠀⠀⢀⠎⠉⠂⢄⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⡰⠁⠀⠀⠀⠀⠁⠢⢀⠀⠀⠀⠀⡆⠀-== NUCLEAR⠀⠀⠀⠀⠀⠀⠀
⠀⣘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠀⡀⡘⠀⠀⠀⠀⠀   TAE ==-
⠰⠁⠁⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠇⠀⠀  ⠀@a1sberg
⡇⠀⠀⠀⠀⠑⠄⡀⠀⠀⠀⠀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢣⠀⠀⠀⠀⠀⠀⠈⠐⠄⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⠆⡀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠉⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
server v.1.1 launching...
⠀⠀⠀⠀⠀
"""

# List to keep track of all connected clients
clients = []

# Directory to store uploaded files
UPLOAD_DIR = "uploads"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Function to broadcast messages to all clients
def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message)
            except:
                clients.remove(client)

# Function to handle file upload
def handle_upload(client_socket, filename, file_size):
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, 'wb') as f:
        bytes_received = 0
        while bytes_received < file_size:
            chunk = client_socket.recv(min(1024, file_size - bytes_received))
            if not chunk:
                break
            f.write(chunk)
            bytes_received += len(chunk)
    broadcast(f"[!] File '{filename}' uploaded successfully.".encode('utf-8'), client_socket)

# Function to handle file download
def handle_download(client_socket, filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        client_socket.send(f"!download {filename}".encode('utf-8'))
        with open(filepath, 'rb') as f:
            while chunk := f.read(1024):
                client_socket.send(chunk)
    else:
        client_socket.send(f"[!] File '{filename}' not found.".encode('utf-8'))

# Function to handle individual client connection
def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                message = message.decode('utf-8')
                if "!upload" in message:
                    _, filename, file_size = message.split()
                    handle_upload(client_socket, filename, int(file_size))
                elif "!download" in message:
                    _, filename = message.split()
                    handle_download(client_socket, filename)
                else:
                    broadcast(message.encode('utf-8'), client_socket)
            else:
                client_socket.close()
                clients.remove(client_socket)
                break
        except:
            client_socket.close()
            clients.remove(client_socket)
            break

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 3844))  # Bind to all interfaces on port 12345
    server_socket.listen(4)

    print(banner)

    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        print(f"[!] Client {client_address} connected.")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    main()
