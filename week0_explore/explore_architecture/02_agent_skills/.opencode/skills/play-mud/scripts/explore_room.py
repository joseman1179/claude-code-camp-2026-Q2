from mud_client import MUDClient
import time

def explore():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        
        # We are in the Immortal Board Room
        # Exits: s
        
        client.send_command("s")
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
    explore()
