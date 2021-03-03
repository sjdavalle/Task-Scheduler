#!/usr/bin/env python3
import socket
import os

def socket_server(socket_path, event):
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
                event.set()
                conn.close()
                break

def getFutureTime(now, additional_minutes) -> str:
    hour = now.hour
    min = now.minute + additional_minutes
    if now.minute == 59:
        min = 0
        hour = now.hour + 1
    return f"{hour:02d}:{min:02d}"