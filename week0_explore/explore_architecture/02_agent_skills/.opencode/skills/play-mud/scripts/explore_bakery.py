from mud_client import MUDClient

def main():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        print("Logged in.")
        
        # Look around first
        client.send_command("look")
        # Assuming the prompt ends with '>'
        response = client.read_until(">")
        print(f"Room Description:\n{response}")
        
        # This is a naive attempt to look for "bakery".
        # Real logic would need to parse room exits, move, etc.
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
