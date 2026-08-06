from state_manager import StateManager

def update_player_location(room_name):
    sm = StateManager()
    player = sm.load_player_state()
    player['current_location'] = room_name
    sm.save_player_state(player)

def add_goal(goal):
    sm = StateManager()
    player = sm.load_player_state()
    if goal not in player['current_goals']:
        player['current_goals'].append(goal)
        sm.save_player_state(player)

def record_observation(room_id, observation):
    sm = StateManager()
    world = sm.load_world_state()
    if room_id not in world['observations']:
        world['observations'][room_id] = []
    world['observations'][room_id].append(observation)
    sm.save_world_state(world)

def add_explored_location(room_id, room_data):
    sm = StateManager()
    world = sm.load_world_state()
    world['explored_locations'][room_id] = room_data
    sm.save_world_state(world)
