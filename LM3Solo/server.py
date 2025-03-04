#!/usr/bin/env python3
import socket
import time
import hmac
import hashlib

# Configuration
HOST = '0.0.0.0'
PORT = 5001
SECRET_KEY = b'super_secret_key'  # Shared secret key

def verify_hmac(received_hmac, data):
    expected_hmac = hmac.new(SECRET_KEY, data, hashlib.sha256).digest()
    return hmac.compare_digest(received_hmac, expected_hmac)

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}")

        conn, addr = server_socket.accept()
        with conn:
            print('Connected by', addr)
            total_received = 0
            start_time = time.time()

            while True:
                packet = conn.recv(1024 * 1024 + 32)  # HMAC(32 bytes) + Data
                if not packet:
                    break

                received_hmac = packet[:32]
                data = packet[32:]

                if verify_hmac(received_hmac, data):
                    total_received += len(data)
                else:
                    print("HMAC verification failed! Data integrity compromised.")

            elapsed = time.time() - start_time
            throughput = total_received / elapsed if elapsed > 0 else 0

            print(f"Received {total_received} bytes in {elapsed:.2f} seconds.")
            print(f"Throughput: {throughput / 1024:.2f} KB/s")

            conn.sendall(b"ACK")

if __name__ == "__main__":
    start_server()
