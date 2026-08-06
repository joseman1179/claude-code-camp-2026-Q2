import json
import os
import collections

class MapNavigator:
    def __init__(self, data_dir="/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/preview/data/world/wld/"):
        self.data_dir = data_dir
        self.graph = {}  # room_id -> {exits: {dir: room_linked}, name: name}
        self.load_map()

    def load_map(self):
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.data_dir, filename), 'r') as f:
                    try:
                        rooms = json.load(f)
                        for room in rooms:
                            room_id = room['id']
                            self.graph[room_id] = {
                                'name': room['name'],
                                'exits': {exit['dir']: exit['room_linked'] for exit in room['exits']}
                            }
                    except (json.JSONDecodeError, KeyError):
                        continue

    def find_path(self, start_room, target_name):
        # BFS to find the path to a room name
        queue = collections.deque([(start_room, [])])
        visited = {start_room}
        
        while queue:
            current_room, path = queue.popleft()
            
            if target_name.lower() in self.graph.get(current_room, {}).get('name', '').lower():
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
