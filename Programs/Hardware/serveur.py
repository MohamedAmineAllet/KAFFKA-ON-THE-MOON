import socket
import time
import keyboard  # using module keyboard
from threading import Timer

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.bind(('', 12345))
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
    connection, adresse = serveur.accept()
    print(f"Nouvelle connexion de {adresse}")

    # Lancer la fonction de contrôle en arrière-plan
    backgroundController(connection)

    if keyboard.is_pressed("enter"):  # if key 'enter' is pressed
        connection.send(bytes('You Pressed A Key!'.encode('utf-8')))
        print("message enter envoyé")

