from mud_client import MUDClient
import time

def solve_bakery():
    client = MUDClient()
    try:
        client.connect("vlade", "clave")
        
        # Simple BFS-like exploration
        queue = ["look"]
        visited = set()
        
        while queue:
            cmd = queue.pop(0)
            client.send_command(cmd)
            time.sleep(1)
            response = client.get_clean_response()
            print(f"Room: {response}")
            
            if "bakery" in response.lower():
                print("Found bakery!")
                client.send_command("list")
                time.sleep(1)
                print(client.get_clean_response())
                return
            
            # Find exits
            exits = []
            if "[ Exits: " in response:
                parts = response.split("[ Exits: ")[1].split(" ]")[0]
                exits = parts.split(" ")
            
            for e in exits:
                if e not in visited and e in ["n", "s", "e", "w", "u", "d"]:
                    visited.add(e)
                    queue.append(e)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    solve_bakery()
