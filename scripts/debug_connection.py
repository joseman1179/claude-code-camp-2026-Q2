import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 4000))

while True:
    try:
        data = s.recv(4096)
        if not data:
            break
        print(data.decode('ascii', errors='ignore'))
        
        # Simple interactive input for now
        # Actually I just want to see the prompt
        
    except Exception as e:
        print(e)
        break
s.close()
