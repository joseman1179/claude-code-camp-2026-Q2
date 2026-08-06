from mud_client import MUDClient
import time
import random

def wander_to_bakery():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        
        # Wander
        for _ in range(50):
            client.send_command("look")
            time.sleep(1)
            response = client.get_clean_response()
            print(f"Current: {response}")
            
            if "bakery" in response.lower():
                print("Found bakery!")
                client.send_command("list")
                time.sleep(2)
                print(client.get_clean_response())
                return
            
            # Wander
            directions = ["n", "s", "e", "w", "u", "d"]
            client.send_command(random.choice(directions))
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    wander_to_bakery()
