import telnetlib
import time
import json
import re

# Liste des appareils (fichier de config et ports)
DEVICES = [
    {"file": "i1_startup-config.cfg","port": 5000},
    {"file": "i2_startup-config.cfg","port": 5001},
    {"file": "i3_startup-config.cfg", "port": 5002},
    {"file": "i4_startup-config.cfg","port": 5003},
    {"file": "i5_startup-config.cfg","port": 5004},
    {"file": "i6_startup-config.cfg", "port": 5005},
    {"file": "i7_startup-config.cfg","port": 5006},
    {"file": "i8_startup-config.cfg","port": 5007},
    {"file": "i9_startup-config.cfg", "port": 5008},
    {"file": "i10_startup-config.cfg","port": 5009},
    {"file": "i11_startup-config.cfg","port": 5010},
    {"file": "i12_startup-config.cfg", "port": 5011},
    {"file": "i13_startup-config.cfg", "port": 5012},
    {"file": "i14_startup-config.cfg","port": 5013},
]

# Charger le fichier JSON
with open('intent.json', 'r') as JSON:
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
        tn.write(b"configure terminal\n"+b"\r\n")
        time.sleep(0.2)

        for command in config_commands:
            command = command.strip()
            if command and command!="!": 
                tn.write(command.encode('ascii') + b"\r\n")
                time.sleep(0.3)
                output = tn.read_very_eager().decode('ascii')  # Lire la sortie
                print(f"Commande : {command}, Réponse : {output}")

        tn.write(b"write"+b"\r\n")
        time.sleep(0.3)
        tn.write(b"y"+b"\r\n")
        print(f"Configuration terminée pour 127.0.0.1:{port}")
    except Exception as e:
        print(f"Erreur avec 127.0.0.1:{port} : {e}")

# Configurer tous les appareils
for device in DEVICES:
    configure_device(device["file"],device["port"])
