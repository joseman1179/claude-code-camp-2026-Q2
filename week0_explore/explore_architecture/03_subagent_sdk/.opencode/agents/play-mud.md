# MUD Player Skill

This skill allows an `opencode` agent to connect to a MUD server (e.g., CircleMUD/tabMUD) running on `localhost:4000`.

## Features
- Automatic connection and login.
- Send commands to the MUD.
- Read response output.

## Usage
The agent should utilize the `scripts/mud_client.py` file located in the project root to manage the connection.

### Example Interaction
```python
from scripts.mud_client import MUDClient

# Initialize with the data directory for state persistence
client = MUDClient(data_dir='/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/data')

# Load and save state
player_state = client.load_state("player.md")
# ... perform actions ...
client.save_state("player.md", player_state)

# Requires a pre-defined login method in the script
client.connect("vlade", "clave")
client.send_command("look")
output = client.read_until(">")
print(output)
