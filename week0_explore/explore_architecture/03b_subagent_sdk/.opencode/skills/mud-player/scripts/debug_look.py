from mud_client import MUDClient

client = MUDClient()
client.connect("vlade", "clave")
client.send_command("look")
print(client.read_response())
client.close()
