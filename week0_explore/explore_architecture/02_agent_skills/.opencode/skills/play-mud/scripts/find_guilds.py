from map_navigator import MapNavigator

nav = MapNavigator()
# Looking for 'Guild Halls'
# The room 106 seems to contain 'Guild Halls'
path = nav.find_path(3005, "Guild Halls") 
print(f"Path to Guild Halls: {path}")
