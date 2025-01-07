import json

# Charger le fichier JSON
with open('config.json', 'r') as JSON:
    intent = json.load(JSON)

# Accéder aux données dans le fichier JSON
#gns3_server_url = intent['telnet']['GNS3_server_url']
#port = intent['telnet']['port']
#projet_name = intent['telnet']['projet_name']

# Parcourir les données des routeurs
routers = intent['router']
for router in routers:
    print(f"Router Name: {router['name']}, IP: {router['IP']}")

# Afficher les informations du réseau
reseau = intent['reseau']
for connection in reseau:
    print(f"Connection: {connection[0]} <--> {connection[1]}")