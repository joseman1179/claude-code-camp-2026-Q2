from mud_client import MUDClient
from map_navigator import MapNavigator, DIR_MAP
import time

def get_current_room_id(nav, client):
    client.send_command("look")
    time.sleep(1)
    response = client.get_clean_response()
    
    print(f"DEBUG: Response:\n{response}")
    
    # Try to find a line that matches a room name in the map
    lines = [line.strip() for line in response.split('\n') if line.strip()]
    
    for line in lines:
        # Ignore lines with status/prompts
        if ">" in line:
            # Maybe the room name is on the same line after >
            parts = line.split('>')
            if len(parts) > 1:
                potential_name = parts[1].strip()
                if potential_name:
                    for room_id, data in nav.graph.items():
                        if potential_name == data['name']:
                            return room_id
        
        # Check against all lines
        for room_id, data in nav.graph.items():
            if line == data['name']:
                return room_id
    
    return None

def auto_navigate_to_bakery():
    client = MUDClient()
    nav = MapNavigator()
    
    try:
        client.connect("vlade", "clave")
        
        # 1. Determine current room
        current_room = get_current_room_id(nav, client)
        if not current_room:
            print("Could not identify current room.")
            return
        print(f"Starting in room: {current_room}")
        
        # 2. Get path to Bakery
        path = nav.find_path(current_room, "Bakery")
        
        if not path:
            print("Could not find path to bakery.")
            return

        # 3. Execute path
        for direction, next_room in path:
            cmd = DIR_MAP[direction]
            print(f"Moving {cmd} to room {next_room}...")
            
            # Pre-emptive action: try opening if a door is mentioned
            client.send_command(f"open {cmd}")
            time.sleep(0.5)
            client.send_command(cmd)
            time.sleep(1)
            response = client.get_clean_response()
            print(response)

        # 4. List menu
        print("At the bakery. Listing menu...")
        client.send_command("list")
        time.sleep(1)
        print(client.get_clean_response())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    auto_navigate_to_bakery()
