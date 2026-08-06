from mud_client import MUDClient
import time
import sys
sys.path.append('/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/scripts/')

def check_score():
    client = MUDClient()
    try:
        print("Connecting...")
        client.connect('Smarty', 'listo')
        print("Connected.")
        
        # Give it a moment after login
        time.sleep(2)
        
        print("Sending 'score' command...")
        client.send_command("score")
        time.sleep(2)
        
        response = client.get_clean_response()
        print("--- SCORE ---")
        print(response)
        print("-------------")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_score()
