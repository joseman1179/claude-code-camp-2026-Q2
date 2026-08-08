from scripts.mud_client import MUDClient
import time

def play_mud():
    client = MUDClient()
    print("Connecting to MUD...")
    client.connect("vlade", "clave")
    
    # Wait for entry
    time.sleep(2)
    
    # 1. Find starting guild
    # Usually 'score' or 'look' might show it, or we need to explore
    print("Checking character status...")
    client.send_command("score")
    print(client.get_clean_response())
    
    # 2. Practice kick
    # Assuming the trainer is near or we need to 'practice' command
    print("Practicing kick...")
    client.send_command("practice kick")
    print(client.get_clean_response())
    
    client.close()

if __name__ == "__main__":
    play_mud()
