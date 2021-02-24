#!/usr/bin/env python3
import socket
import os

def socket_server(socket_path):
    if os.path.exists(socket_path):
        os.remove(socket_path)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.bind(socket_path)
        sock.listen()
        while True:
            conn, _addr = sock.accept()
            data = conn.recv(1024)
            if data:
                print(f"Received data: {data.decode('utf-8')}")
                conn.close()