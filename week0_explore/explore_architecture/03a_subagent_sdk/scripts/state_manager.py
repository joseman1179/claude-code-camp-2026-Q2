import os
import json

class StateManager:
    def __init__(self, data_dir="/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/explore_architecture/02_agent_skills/.opencode/skills/play-mud/data/"):
        self.player_file = os.path.join(data_dir, "player.md")
        self.world_file = os.path.join(data_dir, "world.md")

    def save_player_state(self, state):
        with open(self.player_file, 'w') as f:
            f.write(json.dumps(state, indent=2))

    def load_player_state(self):
        if not os.path.exists(self.player_file) or os.path.getsize(self.player_file) == 0:
            return {}
        with open(self.player_file, 'r') as f:
            return json.load(f)

    def save_world_state(self, state):
        with open(self.world_file, 'w') as f:
            f.write(json.dumps(state, indent=2))

    def load_world_state(self):
        if not os.path.exists(self.world_file) or os.path.getsize(self.world_file) == 0:
            return {}
        with open(self.world_file, 'r') as f:
            return json.load(f)
