import socket
import time
from threading import Timer

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.bind(("localhost", 12345))
serveur.listen(5)
print("le serveur est reeeadyyyyyyyy...")

def backgroundController():
    Message = 'Hello World from the pc'
    print(Message)
    connection.send(bytes(Message.encode('utf-8')))
    Timer(5, backgroundController)



while True:
    connection, addresse = serveur.accept()
    print("Nouvelle connexion de", addresse)


