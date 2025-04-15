import subprocess
import threading
from time import sleep
import dronekit_sitl
import time
import argparse
import math
import collections

import dronekit_sitl
import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
from dronekit import LocationGlobalRelative
import socket
from pymavlink import mavutil

def reaction (pigeonVoyageur) :
    if not (pigeonVoyageur.isdigit()):
        print("Reçu:" ,pigeonVoyageur)
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
                client.sendall(b"piou piou -Over") #Message inutile
                pigeonVoyageur = client.recv(1024)  # Le message reçu
                reaction(pigeonVoyageur)


        except(ConnectionRefusedError, ConnectionResetError, KeyboardInterrupt) as e:  # erreurs de connections
            print("Erreur de connection Client", str(e))
            time.sleep(1)
        finally:
            print("Over and Out")
            client.close()
