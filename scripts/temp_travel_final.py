from scripts.mud_client import MUDClient
import time

def travel_to_guild():
    client = MUDClient()
    client.connect("vlade", "clave")
    time.sleep(2)
    
    # Path found: 'd', 'd', 'w', 'w', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n'
    path = ['d', 'd', 'w', 'w', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n']
    
    print("Navigating to Warrior's Guild...")
    for step in path:
        print(f"Moving {step}...")
        client.send_command(step)
        time.sleep(0.5)
    
    print("Arrived (supposedly). Checking look...")
    client.send_command("look")
    time.sleep(1)
    print(client.get_clean_response())
    
    client.close()

if __name__ == "__main__":
    travel_to_guild()
