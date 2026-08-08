import subprocess

def run_check():
    try:
        # Run the hunger check script
        result = subprocess.run(['python3', 'check_players_hunger.py'], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Failed to run check: {e}")

if __name__ == "__main__":
    run_check()
