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

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("10.185.12.131", 12345))  #localhost

print("Je suis branché!!!")

client.sendall(b"Hello, serveur !")

while True:
    print(client.recv(1024))
    client.close()