import threading
import keyboard
import socket  # ← Import manquant pour utiliser les sockets

"""
Ceci est une classe qui nous permet de tester les envoies de données entre un serveur sur ordinateur et 
un client sur RaspberryPi par exemple
"""

# Création d’un socket TCP (AF_INET pour IPv4, SOCK_STREAM pour TCP)
serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = ''        # Adresse IP du serveur (vide = toutes les interfaces)
PORT = 12345     # Port d'écoute du serveur

# Lier le socket à l'adresse IP et au port
serveur.bind((HOST, PORT))

# Mettre le socket en mode écoute pour accepter des connexions
serveur.listen(1)
print("Le serveur est prêt...")

# Variable partagée entre threads (nécessite un verrou pour éviter les conflits d'accès)
message_lock = threading.Lock()
message = "piou piou 1er du nom"

# Fonction exécutée par un thread qui écoute les frappes clavier
def clavierStalker():
    global message
    while True:
        event = keyboard.read_event()  # Attend une touche du clavier
        if event.event_type == keyboard.KEY_DOWN:  # Si une touche est pressée
            with message_lock:  # Protéger l'accès à la variable partagée
                message = event.name  # Mettre à jour le message à envoyer

# Créer et démarrer le thread qui surveille le clavier
thread_clavier = threading.Thread(target=clavierStalker, daemon=True)
thread_clavier.start()

# Fonction qui envoie le message courant à un client connecté
def envoyerMessage(connection):
    with message_lock:  # Protéger l'accès à la variable partagée
        try:
            connection.send(bytes(message.encode('utf-8')))  # Envoyer le message encodé
        except Exception as e:
            print(f"Erreur d'envoi : {e}")

# Boucle principale du serveur : accepte les connexions des clients
while True:
    connection, addresse = serveur.accept()  # Attendre un nouveau client
    print("Client connecté :", addresse)
    try:
        while True:
            envoyerMessage(connection)  # Envoyer le message à chaque itération
            data = connection.recv(1024)  # Lire les données envoyées par le client
            if not data:  # Si aucune donnée, client déconnecté
                print("Client déconnecté.")
                break
    except Exception as e:
        print("Erreur connexion :", str(e))
    finally:
        connection.close()  # Fermer la connexion proprement
