from mud_client import MUDClient
import time
import sys

# Add the directory to the path if necessary
sys.path.append('/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/scripts/')

print("Connecting...")
client = MUDClient()
client.connect('Smarty', 'listo')
print("Connected as Smarty.")


# Keep the connection alive
while True:
    time.sleep(10)
