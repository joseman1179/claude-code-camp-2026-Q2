
from scripts.mud_client import MUDClient

def check_hunger(username, password):
    client = MUDClient()
    client.connect(username, password)
    client.send_command("score")
    response = client.get_clean_response()
    client.close()
    
    if "hunger" in response.lower() or "hungry" in response.lower():
        # Look for the status
        for line in response.split('\n'):
            if "hunger" in line.lower() or "hungry" in line.lower():
                return f"{username} is: {line.strip()}"
    return f"{username} status does not explicitly mention hunger."

print(check_hunger("Vlade", "password"))
print(check_hunger("Smarty", "password"))
