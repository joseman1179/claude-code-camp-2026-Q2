from map_navigator import MapNavigator, DIR_MAP

def test_map():
    nav = MapNavigator()
    # Try different start rooms
    for start_room in ["0", "1", "2", "100", "99"]:
        path = nav.find_path(start_room, "Bakery")
        if path:
            print(f"Path from {start_room} to bakery: {[DIR_MAP[int(step[0])] for step in path]}")
            return
    print("Path not found from any test room.")

if __name__ == "__main__":
    test_map()
