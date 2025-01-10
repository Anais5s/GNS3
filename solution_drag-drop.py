import json

process_rip= "rip1"
process_ospf= "ospf1"
area_ospf= 0

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
!{int_config}
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
 no ip address
 ip address {int_ip}
 ipv6 enable
 {protocol}
 no shutdown
 !"""

# Charger le fichier JSON
with open('intent.json', 'r') as JSON:
    intent = json.load(JSON)

# Fonction pour générer les adresses IPv6 des interfaces
def generate_ipv6_address(router_id, neighbor_id, suffix):
    # X est le plus petit router_id, Y est l'autre router_id à connecter
    X = min(router_id, neighbor_id)
    Y = max(router_id, neighbor_id)
    return f"2001:{X}:{Y}::{suffix}/64"

def generate_interface_protocol(router_id, neighbor_id, suffix):
    if (router_id==0) or (neighbor_id==0): 	
        neighbor_id=suffix
    if (router_domain[router_id]!=router_domain[neighbor_id]):
        return 
    elif (router_domain[router_id][1]=="RIP"):
        return f"ipv6 rip {process_rip} enable"
    else:
        return f"ipv6 ospf {process_ospf} area {area_ospf}"  #on pourrait avoir un dico area_ospf qui associe un numero d'AS a un numero d'area

    

# Fonction pour générer la configuration d'une interface
def generate_interface_config(router_id, neighbor_id, suffix, inter):
    int_config = interface_template.format(
        int_name=inter,
        int_ip=generate_ipv6_address(router_id, neighbor_id, suffix),
        protocol=generate_interface_protocol(router_id, neighbor_id, suffix)
    )
    return int_config

# Fonction pour générer toutes les configurations des interfaces de tous les routeurs selon les liens existants
def interfaces_config(router_id):
    # all_int_config = {id: "" for id in router_id.values()} # Initialise les dictionnaires pour stocker la configuration des interfaces de tous les routeurs
    all_int_config = {}
    out_domain = {id: "" for id in router_id.values()}
    for id in router_id.values():
        all_int_config[id] = generate_interface_config(0, 0, id, "Loopback0")

    # Collecte des liens entre les routeurs
    for link in intent['reseau']:
        router_name_X, inter_X = link[0]
        router_name_Y, inter_Y = link[1]
        router_X_id = router_id[router_name_X]
        router_Y_id = router_id[router_name_Y]
		
        if router_domain[router_X_id]!=router_domain[router_Y_id]:	#regarde si les 2 routeurs sont dans le meme domaine
             out_domain[router_X_id] += inter_X
             out_domain[router_Y_id] += inter_Y

        all_int_config[router_X_id] += generate_interface_config(router_X_id, router_Y_id, router_X_id, inter_X) # IP pour le routeur X
        all_int_config[router_Y_id] += generate_interface_config(router_Y_id, router_X_id, router_Y_id, inter_Y) # IP pour le routeur Y
	


    return all_int_config, out_domain

# Fonction pour générer la configuration de chaque routeur
def generate_config(router_name, all_int_config):
    int_config = all_int_config[router_id[router_name]]
    return config_template.format(router_name=router_name, int_config=int_config)


router_id = {} # Dictionnaire pour l'identification numérique des routeurs et les interfaces
router_domain = {} # Dictionnaire pour l'appartenance d'un routeur a un domain
# Générer les identifiants de chaque routeur
i=1 # initialisation des id
for domain in intent['domain']:
    # router_domain = intent['domain'][i]['router']
    for router_name in domain['router']:
        router_id[router_name]=i
        i+=1 # nouvel id
        router_domain[router_id[router_name]]=domain['AS'],domain['protocol']

# Récupérer les configurations des interfaces de tous les routeurs selon les liens existants
all_int_config, out_domain = interfaces_config(router_id)


# Générer les fichiers de configuration pour chaque routeur
for router_name in router_id.keys():
    # Générer la configuration pour chaque routeur
    config = generate_config(router_name, all_int_config)
    
    # Sauvegarder la configuration dans un fichier
    filename = f"i{router_id[router_name]}_startup-config.cfg"
    with open(filename, 'w') as f:
        f.write(config)

    print(f"Configuration pour {router_name} générée dans {filename}")
