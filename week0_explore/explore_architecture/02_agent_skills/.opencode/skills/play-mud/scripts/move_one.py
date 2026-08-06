from mud_client import MUDClient
import time

def move_one():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        client.send_command("look")
        time.sleep(1)
        print(client.get_clean_response())
        
        # Try moving South
        client.send_command("s")
        time.sleep(1)
        print(client.get_clean_response())
    except Exception as e:
        print(e)
    finally:
        client.close()

if __name__ == "__main__":
    move_one()
