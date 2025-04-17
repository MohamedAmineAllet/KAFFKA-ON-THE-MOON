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


def backgroundController(connection):
    Message = 'Hello World from the PC'
    print(Message)

    try:
        connection.send(bytes(Message.encode('utf-8')))
    except ConnectionResetError as e:
        print(f"❌ Erreur de connexion (reset): {e}")
    except ConnectionAbortedError as e:
        print(f"❌ Erreur de connexion (abordée): {e}")
    except Exception as e:
        print(f"❌ Autre erreur: {e}")

    Timer(5, backgroundController, [connection]).start()

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
