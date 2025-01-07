from gns3fy import Gns3Connector, Project, Node
import telnetlib
import time

# Configuration de base
GNS3_SERVER_URL = "http://localhost:3080"  
PROJECT_NAME = "GNS3"          				
ROUTER_NAME = "R1"                        #a modifier pour avoir le nom de tous les routeurs
TELNET_PORT = 5000                        # Port telnet du routeur//pareil^

def envoyer_commandes_telnet(host, port, commandes):
    """
    Connecte au routeur via Telnet et envoie des commandes.

    :param host: Adresse du serveur (localhost pour GNS3)
    :param port: Port Telnet du routeur
    :param commandes: Liste des commandes à envoyer
    """
    try:
        # Connexion Telnet
        print(f"Connexion Telnet à {host}:{port}...")
        tn = telnetlib.Telnet(host, port)

        # Attendre l'invite et entrer en mode enable
        tn.read_until(b"Router>")
        tn.write(b"enable\n")

        # Entrer en mode configuration
        tn.write(b"configure terminal\n")

        # Envoyer les commandes de configuration
        for commande in commandes:
            tn.write(commande.encode('ascii') + b"\n")

        # Quitter la configuration
        tn.write(b"end\n")
        tn.write(b"write\n")  # Sauvegarder la configuration
        tn.write(b"exit\n")

        print("Configuration envoyée avec succès.")
        output = tn.read_all().decode('ascii')
        print(output)
    except Exception as e:
        print(f"Erreur lors de l'envoi des commandes Telnet : {e}")

def main():
    # Connexion au serveur GNS3
    gns3_server = Gns3Connector(GNS3_SERVER_URL)

    # Charger le projet
    print(f"Chargement du projet '{PROJECT_NAME}'...")
    project = Project(name=PROJECT_NAME, connector=gns3_server)
    project.get()
    
    # Vérifier si le routeur existe dans le projet
    router = next((node for node in project.nodes if node.name == ROUTER_NAME), None)
    if not router:
        print(f"Routeur '{ROUTER_NAME}' introuvable dans le projet.")
        return

    # Commandes de configuration pour le routeur
    commandes = [
        "interface GigabitEthernet0/0",
        "ipv6 enable",
        "ipv6 address 192.168.1.1::1",
        "no shutdown"
    ]

    # Envoyer les commandes via Telnet
    envoyer_commandes_telnet("localhost", TELNET_PORT, commandes)

main()
