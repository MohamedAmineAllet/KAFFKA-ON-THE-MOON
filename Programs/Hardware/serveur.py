import socket
import threading
import keyboard

# AF_INET → Utilisation d’IPv4  SOCK_STREAM → Utilisation de TCP (connexion fiable)
serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = ''
PORT = 12345

serveur.bind((HOST, PORT))
serveur.listen(1)
print("Le serveur est prêt...")

# Variable partagée entre threads
message_lock = threading.Lock()
message = "piou piou 1er du nom"

def clavierStalker():
    global message
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            with message_lock:
                message = event.name

# Lancer le thread clavier UNE FOIS, en dehors de la boucle principale
thread_clavier = threading.Thread(target=clavierStalker, daemon=True)
thread_clavier.start()

def envoyerMessage(connection):
    with message_lock:
        try:
            connection.send(bytes(message.encode('utf-8')))
        except Exception as e:
            print(f"Erreur d'envoi : {e}")

while True:
    connection, addresse = serveur.accept()
    print("Client connecté :", addresse)
    try:
        while True:
            envoyerMessage(connection)
            data = connection.recv(1024)
            if not data:
                print("Client déconnecté.")
                break
            #print("Reçu :", data.decode())
    except Exception as e:
        print("Erreur connexion :", str(e))
    finally:
        connection.close()
