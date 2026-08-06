from mud_client import MUDClient
client = MUDClient()
client.connect("vlade", "clave")
client.send_command("look")
import time
time.sleep(1)
print(repr(client.read_response()))
client.close()
