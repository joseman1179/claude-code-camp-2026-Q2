from scripts.mud_client import MUDClient

# Assuming TabMUD is running on localhost:4000
client = MUDClient(host='localhost', port=4000)

try:
    print("Connecting...")
    client.connect("Smarty", "listo")
    
    print("Connected. Waiting for prompt...")
    client.read_until(">")
    
    print("Sending 'finger Smarty' command...")
    client.send_command("finger Smarty")
    
    # Read the response until the prompt again
    response = client.read_until(">")
    print("Finger Output:")
    print(response)

except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
