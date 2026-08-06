from scripts.mud_client import MUDClient
import time

def travel_to_guild():
    client = MUDClient()
    client.connect("vlade", "clave")
    time.sleep(2)
    
    print("Navigating...")
    # East from Eastern Foyer
    client.send_command("e")
    time.sleep(1)
    print(client.get_clean_response())
    
    # Need a way to map or just 'look' and explore
    client.send_command("look")
    time.sleep(1)
    print(client.get_clean_response())
    
    client.close()

if __name__ == "__main__":
    travel_to_guild()
