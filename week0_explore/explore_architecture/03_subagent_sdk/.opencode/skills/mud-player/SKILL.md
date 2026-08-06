# MUD Player Skill

This skill allows an `opencode` agent to connect to a MUD server (e.g., CircleMUD/tabMUD) running on `localhost:4000`.

## Features
- Automatic connection and login.
- Send commands to the MUD.
- Read response output.

## Usage
The agent should utilize `scripts/mud_client.py` to manage the connection.

### Example Interaction
```python
from scripts.mud_client import MUDClient

client = MUDClient()
# Requires a pre-defined login method in the script
client.connect("vlade", "clave")
client.send_command("look")
output = client.read_until(">")
print(output)
