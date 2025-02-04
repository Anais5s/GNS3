import json

process_rip= "rip1"
process_ospf= "1"
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
ipv6 unicast-routing
!
ip cef
no ip domain-lookup
no ip icmp rate-limit unreachable
ip tcp synwait 5
!{int_config}
!
{bgp}
{rprotocol}
!
!
!
!
control-plane
!
!
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
 ipv6 address {int_ip}
 ipv6 enable
 {protocol}
 no shutdown
 !"""

bgp_template = """
router bgp {AS}
 bgp router-id {bgp_id}
 bgp log-neighbor-changes
 no bgp default ipv4-unicast
 {neighbor_entries}
 !
 address-family ipv4
 exit-address-family
 !
 address-family ipv6
 {network}
 {neighbor_activations}
 {routemap_activations}
 exit-address-family
 !
 {routemaps}
!
ip forward-protocol nd
!
!
no ip http server
no ip http secure-server
!
!
{static}
!
"""



# Charger le fichier JSON
with open('intent_v1.json', 'r') as JSON:
    intent = json.load(JSON)

# Fonction pour générer les adresses IPv6 des interfaces intra-domain
def generate_ipv6_address_intra(AS, router_id, neighbor_id):
    # X est le plus petit router_id, Y est l'autre router_id à connecter
    X = min(router_id, neighbor_id)
    Y = max(router_id, neighbor_id)
    return f"2001:{AS[2:]}:{X}:{Y}::{router_id}/64"

# Fonction pour générer les adresses IPv6 des interfaces exter-domain
def generate_ipv6_address_extern(router_id, neighbor_id):
    # X est le plus petit router_id, Y est l'autre router_id à connecter
    X = min(router_id, neighbor_id)
    Y = max(router_id, neighbor_id)
    return f"2001:{X}:{Y}::{router_id}/64"

def generate_interface_protocol(router_id, neighbor_id, cost):
    if (router_domain[router_id]!=router_domain[neighbor_id]):
        return ""
    elif (router_domain[router_id][1]=="RIP"):
        return f"ipv6 rip {process_rip} enable"
    else:
        if cost!=0:
            return f"ipv6 ospf {process_ospf} area {area_ospf}\n ipv6 ospf cost {cost}" 
        else:
            return f"ipv6 ospf {process_ospf} area {area_ospf}"
        # On pourrait avoir un dico area_ospf qui associe un numero d'AS a un numero d'area

# Fonction pour générer la configuration d'une interface
def generate_interface_config(AS, router_id, neighbor_id, inter, cost):
    int_config = interface_template.format(
        int_name=inter,
        int_ip=generate_ipv6_address_intra(AS, router_id, neighbor_id) if AS else generate_ipv6_address_extern(router_id, neighbor_id),
        protocol=generate_interface_protocol(router_id, neighbor_id,cost)
    )
    return int_config

def generate_interface_loopback(AS, id):
    int_config = interface_template.format(
        int_name="loopback0",
        int_ip=f"2001:{AS[2:]}::{id}/128",
        protocol=generate_interface_protocol(id,id,0)
    )
    return int_config

# Fonction pour générer toutes les configurations des interfaces de tous les routeurs selon les liens existants
def interfaces_config():
    all_int_config = {} # Initialise les dictionnaires pour stocker la configuration des interfaces de tous les routeurs
    for id in router_id.values():
        all_int_config[id] = generate_interface_loopback(router_domain[id][0], id)
    out_domain = {id: [] for id in router_id.values()}

    # Collecte des liens entre les routeurs
    for link in intent['reseau']:
        router_name_X, inter_X, cost_X= link[0]
        router_name_Y, inter_Y, cost_Y= link[1]
        try:
            router_X_id = router_id[router_name_X]
            router_Y_id = router_id[router_name_Y]
            AS_X = router_domain[router_X_id][0]
            AS_Y = router_domain[router_Y_id][0]

            if AS_X!=AS_Y:	# Regarde si les 2 routeurs sont dans le même domaine
                out_domain[router_X_id].append(router_Y_id)
                out_domain[router_Y_id].append(router_X_id)

                all_int_config[router_X_id] += generate_interface_config(None,  router_X_id, router_Y_id, inter_X,0) # IP pour le routeur X
                all_int_config[router_Y_id] += generate_interface_config(None, router_Y_id, router_X_id, inter_Y,0) # IP pour le routeur Y
            else:
                all_int_config[router_X_id] += generate_interface_config(AS_X,  router_X_id, router_Y_id, inter_X, cost_X) # IP pour le routeur X
                all_int_config[router_Y_id] += generate_interface_config(AS_Y, router_Y_id, router_X_id, inter_Y, cost_Y) # IP pour le routeur Y
        
        except Exception as e:
            print(f"Vérifier les noms de routeur : {e}")
	
    return all_int_config, out_domain

def generate_rprotocol(id):
    redistribute_connected = ""
    if len(out_domain[id])!=0: # Affichage de redistribute connected uniquement en bordure
        redistribute_connected="\n redistribute connected"
    if (router_domain[id][1]=="RIP"):
        return f"ipv6 router rip {process_rip}"+redistribute_connected
    else:
        return f"ipv6 router ospf {process_ospf}\n router-id {id}.{id}.{id}.{id}"+redistribute_connected # Possibilte de creation d'un dico associant un router id a chaque routeur

def generate_bgp(id):
    neighbor_entries = ""
    neighbor_activations = ""
    network=""
    static = ""
    for router in router_domain:
        if router_domain[router][0]==router_domain[id][0] and router!=id:	# Trouve les voisins qui sont dans le meme AS
            AS = router_domain[id][0][2:]
            neighbor_ip=f"2001:{AS}::{router}"	# Adresse loopback du voisin 
            neighbor_entries += f" neighbor {neighbor_ip} remote-as {AS}\n"
            neighbor_entries += f" neighbor {neighbor_ip} update-source Loopback0\n"
            neighbor_activations += f" neighbor {neighbor_ip} activate\n"
        elif router in out_domain[id]: 	# Partie entre 2 AS
            AS=router_domain[router][0][2:]
            neighbor_ip=f"2001:{min(router,id)}:{max(router,id)}::{router}"
            neighbor_entries += f" neighbor {neighbor_ip} remote-as {AS}\n"        
            neighbor_activations += f" neighbor {neighbor_ip} activate\n"
            network += f"network 2001:{router_domain[id][0][2::]}::/32\n "
            static = f"ipv6 route 2001:{router_domain[id][0][2::]}::/32 Null0\n "
    bgp = bgp_template.format(
        AS = router_domain[id][0][2:],
        bgp_id = f"{id}.{id}.{id}.{id}",
        neighbor_entries = neighbor_entries.strip(),
        network = network,
        neighbor_activations = neighbor_activations.strip(),
        routemap_activations=policies_in(id)+policies_out(id),
        static = static,
        routemaps=maps(id)    
	)
    return bgp

def maps(id):
    if out_domain[id]!=[] and router_domain[id][2]=="Self":
        mapClient=f"""route-map mapClient permit 10\n  set local-preference 150\n  set community {router_domain[id][0][2:]}:150\n"""
        mapPeer=f"route-map mapPeer permit 10\n  set local-preference 100\n  set community {router_domain[id][0][2:]}:100\n"
        mapProvider=f"route-map mapProvider permit 10\n  set local-preference 50\n  set community {router_domain[id][0][2:]}:50\n"
        outBound=f"ip community-list standard PEER permit 100:100\n ip community-list standard PROVIDER permit 100:50\n route-map outBound deny 10\n  match community PEER\n route-map outBound deny 20\n  match community PROVIDER\n route-map outBound permit 30\n"
        return f"{mapClient} {mapPeer} {mapProvider} {outBound}"
    else:
        return ""
    
def policies_in(id):
    activations=""
    if router_domain[id][2]=="Self" and out_domain[id]!=[]: #si on est dans notre AS et qu'on est en bordure
        for router in out_domain[id]:
            if router_domain[router][2]=="Client":
                activations += f"neighbor 2001:{id}:{router}::{router} route-map mapClient in\n "
            elif router_domain[router][2]=="Peer":
                activations += f"neighbor 2001:{id}:{router}::{router} route-map mapPeer in\n "
            else:
                activations += f"neighbor 2001:{id}:{router}::{router} route-map mapProvider in\n "
    return activations

def policies_out(id):
    activations=""
    if router_domain[id][2]=="Self" and out_domain[id]!=[]:
        for router in out_domain[id]:
            if router_domain[router][2]=="Peer" or router_domain[router][2]=="Provider":
                activations += f"neighbor 2001:{id}:{router}::{router} route-map outBound out\n "
    return activations


# Fonction pour générer la configuration de chaque routeur
def generate_config(router_name, all_int_config):
    int_config = all_int_config[router_id[router_name]]
    rprotocol = generate_rprotocol(router_id[router_name])
    bgp=generate_bgp(router_id[router_name])
    return config_template.format(router_name=router_name, int_config=int_config, rprotocol=rprotocol, bgp=bgp)

router_id = {} # Dictionnaire pour l'identification numérique des routeurs et les interfaces
router_domain = {} # Dictionnaire pour l'appartenance d'un routeur a un domain
# Générer les identifiants de chaque routeur
i=1 # initialisation des id
for domain in intent['domain']:
    # router_domain = intent['domain'][i]['router']
    for router_name in domain['router']:
        router_id[router_name]=i
        i+=1 # nouvel id
        router_domain[router_id[router_name]]=domain['AS'],domain['protocol'],domain['type']

# Récupérer les configurations des interfaces de tous les routeurs selon les liens existants
all_int_config, out_domain = interfaces_config()

# Générer les fichiers de configuration pour chaque routeur
for router_name in router_id.keys():
    # Générer la configuration pour chaque routeur
    config = generate_config(router_name, all_int_config)
    
    # Sauvegarder la configuration dans un fichier
    filename = f"config\i{router_name[1:]}_startup-config.cfg"
    with open(filename, 'w') as f:
        f.write(config)

    print(f"Configuration pour {router_name} générée dans {filename}")