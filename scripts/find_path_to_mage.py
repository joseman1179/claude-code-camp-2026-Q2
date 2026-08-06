from map_navigator import MapNavigator

nav = MapNavigator()
# 3001 is current location, 3017 is Mages' Guild Entrance
path = nav.find_path(3001, "3017")
print(f"Path: {path}")
