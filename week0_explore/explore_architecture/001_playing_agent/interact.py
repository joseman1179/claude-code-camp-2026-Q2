import socket
import time

def interact():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 4000))
    time.sleep(1)
    s.recv(4096) # Drain

    # login
    s.sendall(b"TestPlayer\n")
    time.sleep(1)
    s.sendall(b"Y\n") # Confirm
    time.sleep(2)
    s.sendall(b"password123\n")
    time.sleep(2)
    
    # Try looking
    s.sendall(b"look\n")
    time.sleep(1)
    
    # Try list
    s.sendall(b"list\n")
    time.sleep(1)
    
    response = s.recv(8192).decode('utf-8', errors='ignore')
    print("Response:", response)
    
    s.close()

if __name__ == "__main__":
    interact()
