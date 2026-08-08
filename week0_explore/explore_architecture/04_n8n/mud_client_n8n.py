import socket
import re
import time

class MUDClient:
    def __init__(self, host='localhost', port=4000):
        self.host = host
        self.port = port
        self.sock = None

    def read_until(self, prompt, timeout=10):
        self.sock.settimeout(timeout)
        data = ""
        while prompt not in data:
            try:
                chunk = self.sock.recv(4096).decode('ascii', errors='ignore')
                if not chunk: break
                data += chunk
                if "Y/N" in data:
                    self.sock.send(b"Y\n")
                    data = ""
            except socket.timeout: break
        return data

    def connect(self, username, password):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.read_until("By what name do you wish to be known?")
        self.sock.send(f"{username}\n".encode('ascii'))
        self.read_until("Password:")
        self.sock.send(f"{password}\n".encode('ascii'))
        self.read_until("Did I get that right")
        self.sock.send(b"Y\n")
        self.read_until(">")
        self.sock.send(b"\n")
        self.read_until("1)")
        self.sock.send(b"1\n")

    def send_command(self, command):
        if self.sock:
            self.sock.send(f"{command}\n".encode('ascii'))

    def read_response(self):
        if self.sock:
            time.sleep(0.5)
            return self.sock.recv(4096).decode('ascii', errors='ignore')
        return ""

    def get_clean_response(self):
        raw = self.read_response()
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', raw)

    def close(self):
        if self.sock: self.sock.close()

def execute(args):
    # args expected: {'host': str, 'port': int, 'username': str, 'password': str, 'command': str}
    # These args are passed by the n8n tool configuration.
    client = MUDClient(args.get('host', 'localhost'), int(args.get('port', 4000)))
    try:
        client.connect(args['username'], args['password'])
        client.send_command(args['command'])
        response = client.get_clean_response()
        client.close()
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
