#!/usr/bin/env python3
import socket
import time
import hmac
import hashlib

# Configuration
HOST = '127.0.0.1'
PORT = 5001
SECRET_KEY = b'super_secret_key'  # Shared secret key

def generate_hmac(data):
    return hmac.new(SECRET_KEY, data, hashlib.sha256).digest()

def run_client():
    message_size = 1024 * 1024  # 1 MB
    num_messages = 10
    total_bytes = message_size * num_messages
    data = b'a' * message_size  # 1 MB of dummy data

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        start_time = time.time()

        for i in range(num_messages):
            hmac_digest = generate_hmac(data)
            client_socket.sendall(hmac_digest + data)  # Send HMAC + data
            print(f"Sent message {i + 1}/{num_messages}")

        client_socket.shutdown(socket.SHUT_WR)

        # Wait for acknowledgment
        ack = client_socket.recv(1024)
        print("Received acknowledgment:", ack.decode())

        elapsed = time.time() - start_time
        throughput = total_bytes / elapsed if elapsed > 0 else 0

        print(f"Sent {total_bytes} bytes in {elapsed:.2f} seconds.")
        print(f"Throughput: {throughput / 1024:.2f} KB/s")

if __name__ == "__main__":
    run_client()
