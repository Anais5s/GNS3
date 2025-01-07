import json

# Template de la configuration de base Cisco
config_template = """
!
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
end
"""
# Template pour la configuration des interfaces
interface_template = """
interface {int_name}
 ip address {int_ip}
 no shutdown
"""

# Charger le fichier JSON
with open('config.json', 'r') as JSON:
    intent = json.load(JSON)

# Fonction pour générer la configuration des interfaces
def generate_interfaces_config(router_int):
    int_config = ""
    for interface in router_int:
        int_config += interface_template.format(
            int_name=interface['name'],
            int_ip=interface['ip']
        )
    return int_config

# Fonction pour générer la configuration de chaque routeur
def generate_config(router_name, router_int):
    int_config = generate_interfaces_config(router_int)
    return config_template.format(router_name=router_name, int_config=int_config)

# Générer les fichiers de configuration pour chaque routeur
for router in intent['router']:
    router_name = router['name']
    router_int = router['interface']
    
    # Générer la configuration pour chaque routeur
    config = generate_config(router_name, router_int)
    
    # Sauvegarder la configuration dans un fichier
    filename = f"{router_name}i1_startup-config.cfg"
    with open(filename, 'w') as f:
        f.write(config)

    print(f"Configuration pour {router_name} générée dans {filename}")