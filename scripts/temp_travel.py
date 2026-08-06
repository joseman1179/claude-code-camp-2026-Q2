from scripts.mud_client import MUDClient
import time

def travel_to_guild():
    client = MUDClient()
    client.connect("vlade", "clave")
    time.sleep(2)
    
    # Assuming I am at ID 102 (Immortal Board Room) based on previous look
    # I need to find my way to Warrior's Guild.
    # Usually this involves 's' (south) to exit the Immortal area.
    
    print("Navigating to Warrior's Guild...")
    client.send_command("s")
    time.sleep(1)
    print(client.get_clean_response())
    
    client.send_command("look")
    time.sleep(1)
    print(client.get_clean_response())
    
    client.close()

if __name__ == "__main__":
    travel_to_guild()
