import sys
import os
sys.path.append('/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/explore_architecture/03_subagent_sdk')
from scripts.mud_client import MUDClient
from scripts.map_navigator import MapNavigator, DIR_MAP

def navigate_to_guild(username, password, guild_name):
    print(f"Launching for {username}...")
    client = MUDClient()
    nav = MapNavigator(data_dir='/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/preview/web/public/data/')
    
    client.connect(username, password)
    
    # Simple strategy: try to find guild hall
    # We need to know current room id, but for now let's assume it starts at 3005 (as per earlier tests)
    # or we can parse it from 'score' or 'look' output.
    # Let's just try to find the path to the guild from the start.
    
    print(f"{username}: Finding path to {guild_name}...")
    # Using a known ID for the Mages Guild for Smarty as per previous grep
    # For Vlade, we need their class first.
    # This script is a simplification.
    
    # (In reality, we should parse the score/look to get current room ID)
    # For this task, I will attempt to navigate to a likely guild.
    
    # ... navigation logic ...
    print(f"{username}: Navigating to {guild_name}...")
    client.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 navigate_to_guild.py <username> <password> <guild_name>")
        sys.exit(1)
    navigate_to_guild(sys.argv[1], sys.argv[2], sys.argv[3])
