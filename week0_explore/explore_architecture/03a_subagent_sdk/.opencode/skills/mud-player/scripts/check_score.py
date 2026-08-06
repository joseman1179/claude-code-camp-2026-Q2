from mud_client import MUDClient
import time

client = MUDClient()
client.connect("vlade", "clave")
time.sleep(2)
client.send_command("score")
print(client.get_clean_response())
client.close()
