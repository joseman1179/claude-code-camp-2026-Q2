from mud_client import MUDClient
import time

def get_bakery_menu():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        
        # Navigate to 3009
        # Assuming we know the path now or can find it
        # Based on previous successful run, just hardcode the movement
        # Or better yet, just try to get to the bakery again.
        
        # Simple navigation for now
        for cmd in ["e", "n"]:
            client.send_command(cmd)
            time.sleep(1)
        
        # We should be at the bakery now.
        # Try different commands to get the menu
        commands_to_try = ["list", "look sign", "ask baker menu"]
        
        for cmd in commands_to_try:
            print(f"--- Trying: {cmd} ---")
            client.send_command(cmd)
            time.sleep(1)
            print(client.get_clean_response())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    get_bakery_menu()
