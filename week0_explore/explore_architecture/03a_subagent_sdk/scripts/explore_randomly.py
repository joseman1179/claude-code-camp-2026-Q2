from mud_client import MUDClient
import time
import random

def explore():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        
        for _ in range(20):
            client.send_command("look")
            time.sleep(0.5)
            response = client.get_clean_response()
            print(response)
            
            if "bakery" in response.lower():
                print("Found it!")
                client.send_command("list")
                time.sleep(1)
                print(client.get_clean_response())
                return
            
            # Simple random walk
            directions = ["n", "s", "e", "w", "u", "d"]
            client.send_command(random.choice(directions))
            time.sleep(0.5)
            print(client.get_clean_response())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    explore()
