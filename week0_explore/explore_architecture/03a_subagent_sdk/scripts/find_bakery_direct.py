from mud_client import MUDClient
import time

def find_bakery_direct():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        
        # Try to find bakery.
        # Often these are in the main city.
        
        # Just look
        client.send_command("look")
        time.sleep(1)
        print(client.get_clean_response())
        
        # Try to search for 'bakery' in exits?
        # Maybe "open bakery"?
        
        # Actually, let me just try a few directions.
        for cmd in ["n", "s", "e", "w"]:
            print(f"Trying {cmd}...")
            client.send_command(cmd)
            time.sleep(1)
            response = client.get_clean_response()
            print(response)
            if "bakery" in response.lower():
                print("Found bakery!")
                client.send_command("list")
                time.sleep(1)
                print(client.get_clean_response())
                return
            
            # Go back
            client.send_command("back" if cmd == "n" else "n" if cmd == "s" else "w" if cmd == "e" else "e")
            time.sleep(1)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    find_bakery_direct()
