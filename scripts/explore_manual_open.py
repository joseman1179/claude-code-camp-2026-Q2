from mud_client import MUDClient
import time

def explore_manual_open():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        
        # Try to open the door north
        client.send_command("open north")
        time.sleep(1)
        print(client.get_clean_response())
        
        # Try to go north
        client.send_command("n")
        time.sleep(1)
        print(client.get_clean_response())
        
        client.send_command("look")
        time.sleep(1)
        print(client.get_clean_response())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    explore_manual_open()
