from map_navigator import MapNavigator
nav = MapNavigator()
# Find all bakeries
for room_id, data in nav.graph.items():
    if "bakery" in data['name'].lower():
        print(f"{room_id}: {data['name']}, Exits: {data['exits']}")
