from mud_client import MUDClient
import time
import sys
sys.path.append('/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/scripts/')

def navigate_to_mage_guild():
    client = MUDClient()
    try:
        client.connect('Smarty', 'listo')
        time.sleep(2)
        
        # Commands to Mages' Guild Entrance
        commands = ['s', 's', 'w', 'w', 's']
        
        for cmd in commands:
            print(f"Moving {cmd}...")
            client.send_command(cmd)
            time.sleep(1)
            response = client.get_clean_response()
            print(response)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    navigate_to_mage_guild()
