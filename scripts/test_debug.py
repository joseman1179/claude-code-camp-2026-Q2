from mud_client import MUDClient
import time
import socket
import sys
sys.path.append('/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/scripts/')

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
        client.sock.send(b"Smarty\n")
        time.sleep(1)
        data = client.sock.recv(4096).decode('ascii', errors='ignore')
        print(f"DEBUG: After Username: {data}")
        
        # Password
        client.sock.send(b"listo\n")
        time.sleep(1)
        data = client.sock.recv(4096).decode('ascii', errors='ignore')
        print(f"DEBUG: After Password: {data}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    debug_connection()
