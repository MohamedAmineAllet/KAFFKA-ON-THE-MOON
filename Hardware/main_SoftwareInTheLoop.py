import subprocess
import dronekit_sitl
import time
import argparse
import math
import collections

from pymavlink import mavutil

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

""" 
# Méthode avec les forces À Revoir 
masse = 2
gravitational = 9.81
coefficient_resistance_air = 0.1
delta_temps = 0.1


def apply_force(vx, vy, vz, teta_X=0, teta_Y=0):
    fx_trainee = vx * -coefficient_resistance_air
    fy_trainee = vy * -coefficient_resistance_air
    fz_trainee = vz * -coefficient_resistance_air

    f_total_poussee = masse * gravitational  # pas sure
    fy_g = -masse * gravitational
    fz_poussee = f_total_poussee * math.cos(teta_X) * math.cos(teta_Y)
    fx_poussee = f_total_poussee * math.sin(teta_X)
    fy_poussee = f_total_poussee * math.sin(teta_Y)

    fx_total = fx_trainee + fx_poussee
    fy_total = fy_trainee + fy_poussee + fy_g
    fz_total = fz_trainee + fz_poussee

    ax = fx_total / masse
    ay = fy_total / masse
    az = fz_total / masse

    new_vx = vx + ax * delta_temps
    new_vy = vy + ay * delta_temps
    new_vz = vz + az * delta_temps
    return new_vx, new_vy, new_vz

"""

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


def setVitesse(vx, vy, vz, duree):
    """
    Déplacer notre véhicule dans une certaine direction en changeant le vecteur vitesse
    :param vx: + Nord / - Sud
    :param vy: + Est / - Ouest
    :param vz: + Bas / - Haut
    Mais pourquoi?
    """
    msg = vehicule.message_factory.set_position_target_local_ned_encode(
        0, # time_boot_ms (not used)
        0, 0, # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0,0,0, # x, y, z positions (not used)
        vx, vy, vz, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0, )  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    # send command to vehicle on 1 Hz cycle
    for x in range(0, duree):
        vehicule.send_mavlink(msg)
        time.sleep(1)


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
        time.sleep(2)

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


""" ****La Mission en question**** """
# vehicle = connectMyCopter() # Pour le Speedou
arm_and_takeoff(10)

#vers le Nord
setVitesse(10,0,0,5)

#vers le Sud
setVitesse(-10,0,0,5)

#vers l'Est
setVitesse(0,10,0,5)

#vers l'Ouest
setVitesse(0,-10,0,5)


vehicule.mode = VehicleMode("RTL")
if vehicule.mode == VehicleMode("RTL"):
    print("Retourne au lauch")

# retourne au lauch

time.sleep(2)

vehicule.close()
sitl.stop()

# Fermer SITL proprement
###### problèmes
# - Le code est malpropre
# - Il n'y a pas de meilleurs moyen pour utiliser les vitesse par exemple deltaTemps plutot que counter?
# -

"""
counter = 0
#  Vx => negative sud, positif nord

def vitesseNord(counter):
    while counter < 2:
        setVitesse(10, 0, 0)
        print("direction Nord")
        time.sleep(1)
        counter = counter + 1
    time.sleep(1)
    counter = 0
def vitesseSud(counter):
    while counter < 2:
        setVitesse(-10, 0, 0)
        print("direction Sud")
        time.sleep(1)
        counter = counter + 1
    time.sleep(1)
    counter = 0


# Vy => negative ouest, positif est
while counter < 2:
    setVitesse(0, 10, 0)
    print("direction est")
    time.sleep(1)
    counter = counter + 1

time.sleep(1)
counter = 0

while counter < 2:
    setVitesse(0, -10, 0)
    print("direction ouest")
    time.sleep(1)
    counter = counter + 1

time.sleep(1)
"""