import socket
import sys
import time

class MUDClient:
    def __init__(self, host='localhost', port=4000):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self, username, password):
        """Connects to the MUD and performs automated login."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        
        # Read until username prompt
        time.sleep(1)
        self.sock.recv(4096)
        
        # Send username
        self.sock.send(f"{username}\n".encode('ascii'))
        
        # Read until password prompt
        time.sleep(1)
        self.sock.recv(4096)
        
        # Send password
        self.sock.send(f"{password}\n".encode('ascii'))
        
        # Read MOTD
        time.sleep(2)
        self.sock.recv(4096)
        
        # Press Return to clear MOTD
        self.sock.send(b"\n")
        
        # Read Menu
        time.sleep(1)
        self.sock.recv(4096)
        
        # Select "1" to enter the game
        self.sock.send(b"1\n")


        
    def send_command(self, command):
        """Sends a command string to the MUD."""
        if self.sock:
            self.sock.send(f"{command}\n".encode('ascii'))

    def read_response(self):
        """Reads output."""
        if self.sock:
            time.sleep(0.5) # Allow MUD to respond
            return self.sock.recv(4096).decode('ascii', errors='ignore')
        return ""

    def get_clean_response(self):
        """Reads output and strips ANSI color codes."""
        import re
        raw = self.read_response()
        # ANSI escape sequence regex
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', raw)

    def close(self):
        """Closes the connection."""
        if self.sock:
            self.sock.close()

