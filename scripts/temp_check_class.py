from scripts.mud_client import MUDClient
import time

def find_guild():
    client = MUDClient()
    client.connect("vlade", "clave")
    time.sleep(2)
    
    # Try 'help' to see if there are guild commands or character class info
    client.send_command("help")
    time.sleep(1)
    print(client.get_clean_response())
    
    # Or just look around
    client.send_command("look")
    time.sleep(1)
    print(client.get_clean_response())
    
    client.close()

if __name__ == "__main__":
    find_guild()
