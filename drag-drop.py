import json

# Template de la configuration de base Cisco
config_template = """!
!
!
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname {router_name}
!
ip cef
no ip domain-lookup
no ip icmp rate-limit unreachable
ip tcp synwait 5
no cdp log mismatch duplex
!
{int_config}
line con 0
 exec-timeout 0 0
 logging synchronous
 privilege level 15
 no login
line aux 0
 exec-timeout 0 0
 logging synchronous
 privilege level 15
 no login
!
!
end"""

# Template pour la configuration des interfaces
interface_template = """
interface {int_name}
 ip address {int_ip}
 no shutdown"""

# Charger le fichier JSON
with open('config.json', 'r') as JSON:
    intent = json.load(JSON)

# Fonction pour générer les adresses IPv6 des interfaces
def generate_ipv6_address(router_id, neighbor_id):
    # X est le plus petit router_id, Y est l'autre router_id à connecter
    X = min(router_id, neighbor_id)
    Y = max(router_id, neighbor_id)
    return f"2001:{X}:{Y}::{router_id}/64"

# Fonction pour générer la configuration d'une interface
def generate_interface_config(router_id, neighbor_id, int):
    int_config = interface_template.format(
        int_name=int,
        int_ip=generate_ipv6_address(router_id, neighbor_id)
    )
    return int_config

# Fonction pour générer toutes les configurations des interfaces de tous les routeurs selon les liens existants
def interfaces_config(router_id):
    all_int_config = {id: "" for id in router_id.values()} # Initialise les dictionnaires pour stocker la configuration des interfaces de tous les routeurs

    # Collecte des liens entre les routeurs
    for link in intent['reseau']:
        router_name_X, int_X, router_name_Y, int_Y = link
        router_X_id = router_id[router_name_X]
        router_Y_id = router_id[router_name_Y]

        all_int_config[router_X_id] += generate_interface_config(router_X_id, router_Y_id, int_X) # IP pour le routeur X
        all_int_config[router_Y_id] += generate_interface_config(router_Y_id, router_X_id, int_Y) # IP pour le routeur Y

    return all_int_config

# Fonction pour générer la configuration de chaque routeur
def generate_config(router_name, all_int_config):
    int_config = all_int_config[router_id[router_name]]
    return config_template.format(router_name=router_name, int_config=int_config)

router_id = {} # Dictionnaire pour l'identification numérique des routeurs et les interfaces
# Générer les identifiants de chaque routeur
for i in range (1,len(intent['router'])+1):
    router_name = intent['router'][i-1]['name']
    router_id[router_name]=i

# Récupérer les configurations des interfaces de tous les routeurs selon les liens existants
all_int_config = interfaces_config(router_id)

# Générer les fichiers de configuration pour chaque routeur
for router in intent['router']:
    router_name = router['name']

    # Générer la configuration pour chaque routeur
    config = generate_config(router_name, all_int_config)
    
    # Sauvegarder la configuration dans un fichier
    filename = f"i{router_id[router_name]}_startup-config.cfg"
    with open(filename, 'w') as f:
        f.write(config)

    print(f"Configuration pour {router_name} générée dans {filename}")