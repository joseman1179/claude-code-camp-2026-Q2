import json
import os
import collections

class MapNavigator:
    def __init__(self, data_dir="/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/preview/web/public/data/"):
        self.data_dir = data_dir
        self.graph = {}  # room_id -> {exits: {dir: room_linked}, name: name}
        self.load_map()

    def load_map(self):
        filename = os.path.join(self.data_dir, "rooms.json")
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                try:
                    data = json.load(f)
                    for room_id, room in data.items():
                        self.graph[room_id] = {
                            'name': room['name'],
                            'exits': {exit['dir']: str(exit['room_linked']) for exit in room.get('exits', [])}
                        }
                except (json.JSONDecodeError, KeyError):
                    pass

    def find_path(self, start_room, target_query):
        # BFS to find the path to a room name or ID
        queue = collections.deque([(start_room, [])])
        visited = {start_room}
        
        while queue:
            current_room, path = queue.popleft()
            
            # Check if current_room matches query (as ID or part of name)
            if target_query == str(current_room) or target_query.lower() in self.graph.get(current_room, {}).get('name', '').lower():
                return path
            
            for direction, neighbor in self.graph.get(current_room, {}).get('exits', {}).items():
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [(direction, neighbor)]))
        return None

# Helper to map direction integers to text
DIR_MAP = {0: 'n', 1: 'e', 2: 's', 3: 'w', 4: 'u', 5: 'd'}

if __name__ == "__main__":
    nav = MapNavigator()
    # Assuming start at 3005 (Temple Square) based on observation,
    # Need to verify current location in the game dynamically, 
    # but for now let's find the path to the Bakery (room 3009)
    path = nav.find_path(3005, "Bakery")
    if path:
        print(f"Path to bakery: {[DIR_MAP[step[0]] for step in path]}")
    else:
        print("Path not found.")
