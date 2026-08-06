from mud_client import MUDClient
import time
import sys
sys.path.append('/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/scripts/')

def get_location():
    client = MUDClient()
    try:
        client.connect('Smarty', 'listo')
        time.sleep(2)
        client.send_command("look")
        time.sleep(1)
        response = client.get_clean_response()
        print(response)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    get_location()
