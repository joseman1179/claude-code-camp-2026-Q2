from map_navigator import MapNavigator

nav = MapNavigator()
# 3001 is current location, 10618 is Guild Halls
path = nav.find_path(3001, "Guild Halls")
print(f"Path: {path}")
