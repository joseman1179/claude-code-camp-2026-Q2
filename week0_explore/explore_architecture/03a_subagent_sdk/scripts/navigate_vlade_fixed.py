import sys
import os
sys.path.append('/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/explore_architecture/03_subagent_sdk')
from scripts.mud_client import MUDClient
from scripts.state_manager import StateManager
from scripts.map_navigator import MapNavigator, DIR_MAP

# Setup
# Need to dynamically determine current room_id. For now, assume known start or parse it.
# Based on earlier output, starting room is "Coffee Alcove" (need to map this to ID)
# Let's assume for now we start at 3005 as per map_navigator.py example
DATA_DIR = '/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/explore_architecture/03_subagent_sdk/data/'
ROOMS_DIR = '/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/preview/web/public/data/'

state_manager = StateManager(data_dir=DATA_DIR)
client = MUDClient()
nav = MapNavigator(data_dir=ROOMS_DIR)

# Connect and Login
client.connect("Vlade", "clave")

# Assume current room ID is 3005 for testing the pathfinding
current_room = "3001" # Temple
target = "3009" # Bakery

print(f"Finding path from {current_room} to {target}...")
path = nav.find_path(current_room, target)

if path:
    directions = [DIR_MAP[int(step[0])] for step in path]
    print(f"Path: {directions}")
    
    # Execute path
    for direction in directions:
        print(f"Moving {direction}...")
        client.send_command(direction)
        response = client.get_clean_response()
        print(response)
        
        if "closed" in response.lower():
            print(f"Door closed, attempting to open {direction}...")
            client.send_command(f"open {direction}")
            print(client.get_clean_response())
            
            print(f"Retrying move {direction}...")
            client.send_command(direction)
            print(client.get_clean_response())
        
    print("Arrived.")
else:
    print("Path not found.")

client.close()
