from scripts.mud_client import MUDClient
from scripts.map_navigator import MapNavigator, DIR_MAP
import time

def navigate_to_guild():
    client = MUDClient()
    client.connect("vlade", "clave")
    
    # We need to find current room ID.
    # The client doesn't seem to have a simple 'get_room_id'
    # but the logs often show it or we can infer it.
    
    # Based on previous look output:
    # "God Hall, East" [Exits: n e s w u ]
    
    # Let's assume we are in the God/Immortal area, let's find the way to the main game map
    # A common exit from Immortal area is 'd' or 's'.
    
    print("Navigating to Warrior's Guild...")
    
    # Let's try to get to a known room ID if possible, or just explore
    # Using the navigator to find path from a known starting room to Warrior's Guild
    
    # Need to know where we are.
    # If we can't find ID, we can't use MapNavigator effectively for pathfinding
    
    client.close()

if __name__ == "__main__":
    navigate_to_guild()
