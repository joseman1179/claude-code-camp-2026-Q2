import sys
import subprocess

# Simple script to run the check
try:
    result = subprocess.run([sys.executable, 'check_players_hunger.py'], capture_output=True, text=True)
    print("Output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
except Exception as e:
    print(f"An error occurred: {e}")
