import socket
import threading
import sys
import argparse
import os

client = ""

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                message = message.decode('utf-8')
                if "!download" in message:
                    _, _, filename = message.split()
                    handle_download(client_socket, filename)
                else:
                    print(message)
            else:
                client_socket.close()
                break
        except:
            client_socket.close()
            break

def handle_download(client_socket, filename):
    filepath = os.path.join("downloads", filename)
    os.makedirs("downloads", exist_ok=True)
    with open(filepath, 'wb') as f:
        bytes_received = 0
        while True:
            chunk = client_socket.recv(min(1024, file_size - bytes_received))
            if not chunk:
                break
            f.write(chunk)
            bytes_received += len(chunk)
    print(f"(!) File '{filename}' downloaded successfully.")

def main():
    parser = argparse.ArgumentParser(description="LAN Group Chat Server")
    parser.add_argument("host", help="Host IP address to bind the server")
    parser.add_argument("name", help="Identifier name to use")

    args = parser.parse_args()
    client = args.name

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((args.host, 3844))  # Connect to the server

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        message = input().lower()

        if message == '!exit':
            client_socket.close()
            break
        elif "!upload" in message:
            _, filepath = message.split()
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                file_size = os.path.getsize(filepath)
                client_socket.send(f"!upload {filename} {file_size}".encode('utf-8'))
                with open(filepath, 'rb') as f:
                    while chunk := f.read(1024):
                        client_socket.send(chunk)
                print(f"(!) File '{filename}' uploaded successfully.")
        else:
            client_socket.send(("<" + client + "> ").encode('utf-8') + message.encode('utf-8'))

if __name__ == "__main__":
    main()
