from scripts.mud_client import MUDClient
import time

def check_status():
    client = MUDClient()
    client.connect("vlade", "clave")
    time.sleep(2)
    
    # Try 'who' to see class
    client.send_command("who")
    time.sleep(1)
    print(client.get_clean_response())
    
    client.close()

if __name__ == "__main__":
    check_status()
