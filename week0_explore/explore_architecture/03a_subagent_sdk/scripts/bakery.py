from mud_client import MUDClient
import time

def explore_hall():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        
        # Navigate from Foyer to God Hall East Extension
        client.send_command("e")
        time.sleep(1)
        
        # In God Hall East Extension, look for "bakery" door
        client.send_command("look")
        time.sleep(1)
        print(client.read_response())
        
        # List all items/doors in room
        client.send_command("inventory") # Just in case
        time.sleep(0.5)
        
        # Maybe it's east?
        client.send_command("open east")
        time.sleep(0.5)
        client.send_command("e")
        time.sleep(1)
        
        response = client.read_response()
        print(response)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    explore_hall()
