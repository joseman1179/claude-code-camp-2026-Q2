import time
import json
import os
import re
from mud_client import MUDClient
from state_manager import StateManager
from state_helper import update_player_location, record_observation, add_explored_location

def scout():
    client = MUDClient()
    sm = StateManager()
    visited_rooms = set()
    
    try:
        client.connect("vlade", "clave")
        
        # Explore for a while
        for _ in range(100):
            client.send_command("look")
            time.sleep(1)
            response = client.get_clean_response()
            
            # Extract Room Name
            lines = response.split('\r\n')
            room_name = "Unknown"
            for i, line in enumerate(lines):
                if ">" in line:
                    if len(line.split(">")) > 1 and line.split(">")[1].strip():
                        room_name = line.split(">")[1].strip()
                    elif i + 1 < len(lines):
                        room_name = lines[i+1].strip()
                    break
            
            visited_rooms.add(room_name)
            
            # Extract Exits
            exits_match = re.search(r'\[ Exits: (.*?) \]', response)
            exits_text = exits_match.group(1) if exits_match else ""
            exits = [e.strip() for e in exits_text.split() if e.strip()]
            
            # Update State
            update_player_location(room_name)
            add_explored_location(room_name, {"exits": exits, "desc": response})
            
            print(f"Scouting: {room_name}, Exits: {exits}")
            
            if "minotaur" in response.lower():
                print(f"Found Massive Minotaur in {room_name}!")
                break
            
            # Navigate
            moved = False
            for exit in exits:
                direction = exit.replace('(', '').replace(')', '')
                
                # Try to move
                client.send_command(direction)
                time.sleep(0.5)
                # If failed, try to open
                response_after_move = client.get_clean_response()
                if "closed" in response_after_move.lower():
                    client.send_command(f"open {direction}")
                    client.send_command(direction)
                    time.sleep(0.5)
                
                # If successful move, break and loop again
                # Check if the room name changed
                client.send_command("look")
                time.sleep(0.5)
                response_look = client.get_clean_response()
                if room_name not in response_look:
                    moved = True
                    break
            
            if not moved:
                # Backtrack or random direction
                pass
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    scout()
