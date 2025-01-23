import telnetlib
import time
import json

# Liste des appareils (fichier de config et ports)
DEVICES = [
    {"file": "i1_startup-config.cfg","port": 5005},
    {"file": "i2_startup-config.cfg","port": 5007},
    {"file": "i3_startup-config.cfg", "port": 5000},
    {"file": "i4_startup-config.cfg","port": 5001},
    {"file": "i5_startup-config.cfg","port": 5002},
    {"file": "i6_startup-config.cfg", "port": 5003},
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
        tn.read_until(b"Press RETURN to get started!",timeout=5)
        tn.write(b"\r\n")
        tn.write(b"enable\n")
        tn.write(b"configure terminal\n")
        time.sleep(1)

        for command in config_commands:
            tn.write(command.strip().encode('ascii') + b"\n")
            time.sleep(0.2)

        tn.write(b"end\n")
        tn.write(b"write\n")
        tn.write(b"exit\n")
        print(f"Configuration terminée pour 127.0.0.1:{port}")
    except Exception as e:
        print(f"Erreur avec 127.0.0.1:{port} : {e}")

# Configurer tous les appareils
for device in DEVICES:
    configure_device(device["file"],device["port"])
