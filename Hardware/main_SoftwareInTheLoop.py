import subprocess
import dronekit_sitl
import argparse
import collections

if not hasattr(collections, 'MutableMapping'):
    import collections.abc

    collections.MutableMapping = collections.abc.MutableMapping
import dronekit_sitl
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

print("Tous le monde est prêt? On met les voiiiles...")

# Commencer la simulation
sitl = dronekit_sitl.start_default()
connection_string = 'tcp:127.0.0.1:5760'  # Port ouvert par SITL

print(f"La chaîne de connection du véhicule: {connection_string}")
# Se connecter au véhicule simulé
vehicule = connect(connection_string, wait_ready=True)

# IMPORTANT NB: on a 10s pour connecter mission planner et mettre manuelement le mode guided (***Pourquoi dronekit ne le fait pas? Compatibilité?)
for i in range(5, 0, -1):
    print(i)
    time.sleep(1)

# 2 Lancer Mission Planner automatiquement
"""
mission_planner_path = "C:\\Program Files (x86)\\Mission Planner\\MissionPlanner.exe"
subprocess.Popen([mission_planner_path])
# Attendre que Mission Planner se lance
time.sleep(5) 
"""

# Se connecter au Firmware soit le Flight Controller et ardupilot
"""
def connectMyCopter():
    parser = argparse.ArgumentParser(description="commands")
    parser.add_argument("--connect", default=connection_string)
    args = parser.parse_args()
    vehicle = connect(connection_string, wait_ready=True)
    return vehicle
"""


# Méthode pour armer et décoller à une altitude donnée
def arm_and_takeoff(target_altitude):
    while not vehicule.is_armable:
        print("wait for vehicle to be armed")
        time.sleep(1)

    # Changer le mode du drone en "GUIDED"
    vehicule.mode = VehicleMode("GUIDED")

    # Attendre que le mode soit bien activé
    while vehicule.mode.name != "GUIDED":
        print("- En attente du changement de mode en GUIDED...")
        time.sleep(1)

    print("Mode actuel:" + vehicule.mode.name)

    # Vérifier si le drone est armable avant de l'armer
    while not vehicule.is_armable:
        time.sleep(1)

    # Armer le drone
    vehicule.armed = True

    # Attendre que le drone soit effectivement armé
    while not vehicule.armed:
        time.sleep(1)

    print("- Véhicule armé et prêt à fonctionner !")

    # **Fonctionalité DroneKit pour le décollage**
    vehicule.simple_takeoff(target_altitude)

    while True:
        print("Current Altitude: %d" % vehicule.location.global_relative_frame.alt)
        if vehicule.location.global_relative_frame.alt > target_altitude:
            break
        time.sleep(1)
    print("Target altitude reached")
    return None


""" La Mission en question """
# vehicle = connectMyCopter() # Pour le Speedou
arm_and_takeoff(10)

vehicule.close()
sitl.stop()

# Fermer SITL proprement
