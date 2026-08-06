from mud_client import MUDClient
import time

def find_bakery():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        
        # From Eastern Foyer (n, e, s, w)
        # Go East
        client.send_command("e")
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
    find_bakery()
