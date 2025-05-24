import collections
import subprocess
import threading
from time import sleep
import dronekit_sitl
import time
import argparse
import math

# DroneKit : contrôle de drones avec ArduPilot via MAVLink
from dronekit import connect, VehicleMode, LocationGlobalRelative, APIException, Command
from pymavlink import mavutil
import socket

# Correction de compatibilité pour certaines versions de Python
collections.MutableMapping = collections.abc.MutableMapping

"""
Ceci est un bout de code qui nous a permis d'exprimenter avec les données reçues d'un serveur
C'est la base du code qui se retrouve sur le rpi 
"""
# ********** LES FONCTIONS ********** #

def connectMyCopter():
    """
    Connexion à un véhicule ArduPilot via DroneKit.
    Si aucun paramètre --connect n'est fourni, lance un simulateur SITL.
    :return: Objet 'vehicule' représentant le drone connecté.
    """
    parser = argparse.ArgumentParser(description='commands')
    parser.add_argument('--connect')
    args = parser.parse_args()

    connection_string = args.connect

    if not connection_string:
        sitl = dronekit_sitl.start_default()
        connection_string = sitl.connection_string()

    vehicule = connect(connection_string, wait_ready=True)

    return vehicule


def reaction(pigeonVoyageur):
    """
    Interprète les messages reçus du serveur.
    Si le message est un chiffre, effectue une action simulée.
    Sinon, affiche le message tel quel.
    """
    if not (pigeonVoyageur.isdigit()):
        print("Reçu:", pigeonVoyageur)
    else:
        try:
            pigeonVoyageur = int(pigeonVoyageur)
            match pigeonVoyageur:
                case 1:
                    print("up")
                case 2:
                    print("down")
                case 3:
                    print("left")
                case 4:
                    print("right")
        except Exception:
            print("Le Message n'est pas un Entier")
        finally:
            print("******************")


# ********** CLIENT TCP ********** #

while True:
    try:
        # Création du socket client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", 12345))  # Connexion au serveur local
        time.sleep(1)

        while True:
            client.sendall(b"piou piou -Over")  # Envoi d’un message inutile au serveur
            pigeonVoyageur = client.recv(1024)  # Réception d’un message du serveur
            pigeonVoyageur = pigeonVoyageur.decode('utf-8')  # Décodage en UTF-8
            reaction(pigeonVoyageur)  # Traitement du message reçu

    except (ConnectionRefusedError, ConnectionResetError, KeyboardInterrupt) as e:
        print("Erreur de connection Client", str(e))
        time.sleep(1)

    finally:
        print("Over and Out")
        client.close()  # Fermeture propre de la socket
