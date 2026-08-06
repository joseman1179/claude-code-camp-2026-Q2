from mud_client import MUDClient
from state_manager import StateManager
from state_helper import update_player_location, record_observation, add_explored_location
import time

def explore_manual():
    client = MUDClient()
    
    try:
        client.connect("vlade", "clave")
        
        # Look and track
        client.send_command("look")
        time.sleep(1)
        response = client.get_clean_response()
        print(response)
        
        # Basic parsing (naive)
        lines = response.split('\n')
        room_name = lines[0].strip()
        
        # Track info
        update_player_location(room_name)
        add_explored_location(room_name, {"desc": response})
        record_observation(room_name, "Visited.")
        
        print(f"Updated state for room: {room_name}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    explore_manual()
