import telnetlib
import time
import json

# Charger le fichier JSON
with open('intent_v3.2.json', 'r') as JSON:
    intent = json.load(JSON)


# Fonction pour configurer un appareil
def configure_device(CONFIG_FILE,port):
    with open(CONFIG_FILE, "r") as f:
        config_commands = f.readlines()
    try:
        tn = telnetlib.Telnet("127.0.0.1", port)
        print(f"Connexion établie avec 127.0.0.1:{port}")
        tn.read_until(b"Press RETURN to get started!",timeout=5)
        tn.write(b"\r\n")
        tn.write(b"enable"+b"\r\n")        
        time.sleep(0.2)
        tn.write(b"configure terminal"+b"\r\n")
        time.sleep(0.2)

        for command in config_commands:
            command = command.strip()
            if command and command!="!": 
                tn.write(command.encode('ascii') + b"\r\n")
                output = tn.read_very_eager().decode('ascii')  # Lire la sortie
                time.sleep(0.1)

        # tn.write(b"write"+b"\r\n")
        # time.sleep(0.3)
        # tn.write(b"y"+b"\r\n")
        print(f"Configuration terminée pour 127.0.0.1:{port}")
    except Exception as e:
        print(f"Erreur avec 127.0.0.1:{port} : {e}")

# Configurer tous les appareils
for connect in intent["telnet"]["port"]:
    name,port=connect
    configure_device(f"config\i{name[1:]}_startup-config.cfg",port)
