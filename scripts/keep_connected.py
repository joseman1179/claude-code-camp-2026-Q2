from scripts.mud_client import MUDClient
import socket
import time
import sys

def keep_connected():
    client = MUDClient()
    
    print("Connecting to MUD...")
    client.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.sock.connect((client.host, client.port))
    client.sock.settimeout(5)
    
    def safe_recv():
        try:
            return client.sock.recv(4096)
        except socket.timeout:
            return b""
            
    # Username
    print("Sending username...")
    client.sock.send(b"vlade\n")
    time.sleep(1)
    safe_recv()
    
    # Password
    print("Sending password...")
    client.sock.send(b"clave\n")
    time.sleep(1)
    safe_recv()
    
    # Y/N for password
    print("Sending Y for password confirmation...")
    client.sock.send(b"Y\n")
    time.sleep(1)
    safe_recv()
    
    # MOTD
    print("Sending MOTD...")
    client.sock.send(b"\n")
    time.sleep(1)
    safe_recv()
    
    # Menu
    print("Sending menu choice 1...")
    client.sock.send(b"1\n")
    time.sleep(1)
    safe_recv()
    
    print("Connected! Keeping the session open.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing connection.")
        client.close()

if __name__ == "__main__":
    keep_connected()
