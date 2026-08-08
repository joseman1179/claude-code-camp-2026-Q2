from mud_client import MUDClient
import time

def debug_connection():
    client = MUDClient()
    try:
        # Start connection
        client.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.sock.connect(('localhost', 4000))
        
        # Read initial prompt
        time.sleep(1)
        data = client.sock.recv(4096).decode('ascii', errors='ignore')
        print(f"DEBUG: Initial: {data}")
        
        # Username
        client.sock.send(b"vlade\n")
        time.sleep(1)
        data = client.sock.recv(4096).decode('ascii', errors='ignore')
        print(f"DEBUG: After Username: {data}")
        
        # Password
        client.sock.send(b"clave\n")
        time.sleep(1)
        data = client.sock.recv(4096).decode('ascii', errors='ignore')
        print(f"DEBUG: After Password: {data}")
        
        # If MOTD
        time.sleep(1)
        client.sock.send(b"\n")
        data = client.sock.recv(4096).decode('ascii', errors='ignore')
        print(f"DEBUG: After MOTD: {data}")
        
        # Menu
        client.sock.send(b"1\n")
        time.sleep(1)
        data = client.sock.recv(4096).decode('ascii', errors='ignore')
        print(f"DEBUG: After Menu: {data}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

import socket
if __name__ == "__main__":
    debug_connection()
