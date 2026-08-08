import json
import os

data_dir = "/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/preview/data/world/wld/"
for filename in os.listdir(data_dir):
    if filename.endswith(".json"):
        with open(os.path.join(data_dir, filename), 'r') as f:
            try:
                rooms = json.load(f)
                for room in rooms:
                    if 'guild' in room['name'].lower() or 'guild' in room.get('desc', '').lower():
                        print(f"Found Guild: {room['name']} (ID: {room['id']})")
            except:
                continue
