import collections
import subprocess
import threading
from time import sleep
import dronekit_sitl
import time
import argparse
import math

import dronekit_sitl
from dronekit import connect, VehicleMode, LocationGlobalRelative, APIException, Command
import time
import socket
import argparse
from pymavlink import mavutil

collections.MutableMapping = collections.abc.MutableMapping


# **********LES FONCTIONS**********#

def connectMyCopter():
    """
    Se connecter à un véhicule configuré avec Ardupilot via Mavlink
    :return: Un objet vehicule
    """
    parser = argparse.ArgumentParser(description='commands')
    parser.add_argument('--connect')
    args = parser.parse_args()

    connection_string = args.connect

    if not connection_string:
        import dronekit_sitl
        sitl = dronekit_sitl.start_default()
        connection_string = sitl.connection_string()

    vehicule = connect(connection_string, wait_ready=True)

    return vehicule



def reaction(pigeonVoyageur):
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

        except(Exception):
            print("Le Message n'est pas un Entier")
        finally:
            print("******************")


while True:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", 12345))  # localhost
        time.sleep(1)

        while True:
            client.sendall(b"piou piou -Over")  # Message inutile
            pigeonVoyageur = client.recv(1024)  # Le message reçu
            reaction(pigeonVoyageur)


    except(ConnectionRefusedError, ConnectionResetError, KeyboardInterrupt) as e:  # erreurs de connections
        print("Erreur de connection Client", str(e))
        time.sleep(1)
    finally:
        print("Over and Out")
        client.close()
