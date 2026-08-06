import socket
import sys
import time

class MUDClient:
    def __init__(self, host='localhost', port=4000):
        self.host = host
        self.port = port
        self.sock = None

    def read_until(self, prompt, timeout=10):
        """Reads until a specific prompt is found."""
        self.sock.settimeout(timeout)
        data = ""
        while prompt not in data:
            try:
                chunk = self.sock.recv(4096).decode('ascii', errors='ignore')
                if not chunk:
                    break
                data += chunk
                
                # Automatically handle Yes/No confirmation
                if "Y/N" in data:
                    print("DEBUG: Yes/No detected, sending Y")
                    self.sock.send(b"Y\n")
                    # Clear data to avoid infinite loop
                    data = ""
            except socket.timeout:
                break
        return data
    
    def connect(self, username, password):
        """Connects to the MUD and performs automated login."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        
        # Read until username prompt
        self.read_until("By what name do you wish to be known?")
        self.sock.send(f"{username}\n".encode('ascii'))
        
        # Read until password prompt
        self.read_until("Password:")
        self.sock.send(f"{password}\n".encode('ascii'))
        
        # Handle Y/N confirmation for password
        self.read_until("Did I get that right")
        self.sock.send(b"Y\n")
        
        # MOTD
        self.read_until(">")
        self.sock.send(b"\n")
        
        # Menu
        self.read_until("1)")
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

