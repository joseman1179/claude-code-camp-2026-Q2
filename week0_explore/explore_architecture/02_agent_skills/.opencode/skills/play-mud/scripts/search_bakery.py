import json
with open('/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/preview/web/public/data/rooms.json', 'r') as f:
    rooms = json.load(f)
    for room_id, room in rooms.items():
        if "bakery" in room['name'].lower() or "bakery" in room['desc'].lower():
            print(f"Found {room_id}: {room['name']}")
