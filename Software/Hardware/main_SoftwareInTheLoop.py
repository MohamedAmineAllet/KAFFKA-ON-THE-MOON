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
from dronekit import LocationGlobalRelative

print("Tous le monde est prêt? On met les voiiiles...")

# Commencer la simulation
sitl = dronekit_sitl.start_default()
connection_string = 'tcp:127.0.0.1:5760'  # Port ouvert par SITL

print(f"La chaîne de connection du véhicule: {connection_string}")
# Se connecter au véhicule simulé
vehicule = connect(connection_string, wait_ready=True)


def setGuidedMode():
    """
    Forcer le mode guide via mavlink
    """
    vehicule._master.mav.set_mode_send(
        vehicule._master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        4  # Mode GUIDED = 4 en ArduPilot
    )
    time.sleep(1)


def setReturnToLauch():
    "Forcer le mode RTL via mavLink"
    print("on retourne au lauch")
    vehicule._master.mav.set_mode_send(
        vehicule._master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        6  # Mode GUIDED = 4 en ArduPilot
    )
    time.sleep(1)


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


def positionConversion(ned, yaw):
    """ Convertit la position NED en Body Frame (Avant, Droite, Bas). """
    nord, est, bas = ned

    avant = nord * math.cos(yaw) + est * math.sin(yaw)
    droite = -nord * math.sin(yaw) + est * math.cos(yaw)
    return [avant, droite, bas]  # Bas reste inchangé

    # Récupérer la position NED
    position_ned = vehicule.location.local_frame  # [Nord, Est, Bas] en mètres
    yaw = vehicule.attitude.yaw  # Orientation (yaw) en radians

    # Convertir en Body Frame
    position_body = ned_vers_body_position([position_ned.north, position_ned.east, position_ned.down], yaw)

    # Afficher la position en Body Frame
    return ("Position en Body Frame:", position_body)


def setVitesse(vx, vy, vz, duree):
    """
    Déplacer notre véhicule dans une certaine direction en changeant le vecteur vitesse
    :param vx: + Nord / - Sud      ||  + Devant / - Derrière
    :param vy: + Est / - Ouest     || + Droite / - Gauche
    :param vz: + Bas / - Haut      || + Bas / - Haut
    Système de coordonnées conventionel NED  ||  Système de coordonnées Relatve au drone <-
    """
    msg = vehicule.message_factory.set_position_target_local_ned_encode(
        0,  # time_boot_ms (not used)
        0, 0,  # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_NED,  # FRAME_BODY_NED pour se déplacer Body Frame
        0b0000111111000111,  # type_mask (only speeds enabled)
        0, 0, 0,  # x, y, z positions (not used)
        vx, vy, vz,  # x, y, z velocity in m/s
        0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0, )  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    # send command to vehicle on 1 Hz cycle
    for x in range(0, duree):
        vehicule.send_mavlink(msg)
        time.sleep(1)
        # Afficher la position relative au vehicule
        position_ned = vehicule.location.local_frame  # [North, East, Down] en mètres
        yaw = vehicule.attitude.yaw  # Orientation du drone (yaw) en radians
        latitude = vehicule.location.global_frame.lat  # Current latitude
        longitude = vehicule.location.global_frame.lon  # Current longitude
        altitude = vehicule.location.global_relative_frame.alt  # Altitude
        position_body = positionConversion([position_ned.north, position_ned.east, position_ned.down], yaw)
        print(position_ned)
        print(" latitude : %.6f" % latitude + " longitude : %.6f" % longitude + " altidude: %.2f m" % altitude)


# Méthode pour armer et décoller à une altitude donnée
def arm_and_takeoff(target_altitude):
    while not vehicule.is_armable:
        print("wait for vehicle to be armed")
        time.sleep(1)

    # Changer le mode du drone en "GUIDED"
    while vehicule.mode.name != 'GUIDED':
        print("- En attente du changement de mode en GUIDED...")
        setGuidedMode()
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

def ajouter_point(latitude, longitude, altitude):
    return LocationGlobalRelative(latitude, longitude, altitude)


def suivre_trajectoire(vehicule, point):
    setGuidedMode()

    print(f"Navigation vers {point.lat}, {point.lon}, {point.alt}m")

    vehicule.simple_goto(point, groundspeed=10)

    while True:  # permet de calculer la distance restante jusqu'a notre point
        position_actuelle = vehicule.location.global_relative_frame
        distance = math.sqrt(
            (point.lat - position_actuelle.lat) ** 2 +
            (point.lon - position_actuelle.lon) ** 2
        ) * 111320  # Convertir degrés -> mètres, 1 degres = 111320m

        print(f" Distance restante : {distance:.2f}m")
        if distance < 2:
            print("trajectoire atteinte !")
            break
        time.sleep(2)


def voler_en_cercle(rayon, vitesse, boucles=1, duree=10):
    print("demarrage du vol en cercle")
    points = 24
    angle_step = 2 * math.pi / points
    for loop in range(0, boucles):
        for point in range(points):
            angle = point * angle_step
            vx = vitesse * math.cos(angle)  # Vitesse sur l'axe Nord/Sud
            vy = vitesse * math.sin(angle)  # Vitesse sur l'axe Est/Ouest
            vz = 0  # Altitude constante
            setVitesse(vx, vy, vz, duree)
    print("vole en cercle terminer")
    setReturnToLauch()
    """
            nb_points = int(duree / 0.5)
            angle_incrementer = (2 * math.pi)

            for i in range(nb_points):
                angle = i * angle_incrementer
                vx = vitesse * math.cos(angle)
                vy = vitesse * math.sin(angle)
                setVitesse(vx, vy, 0, 1)
            print("vole en cercle terminer")
            setReturnToLauch()
            """


""" ****La Mission en question**** """
# vehicle = connectMyCopter() # Pour le Speedou
arm_and_takeoff(10)

# vers le Nord
setVitesse(10, 0, 0, 5)

# vers le Sud
setVitesse(-10, 0, 0, 5)

# vers l'Est
setVitesse(0, 10, 0, 5)

# vers l'Ouest
setVitesse(0, -10, 0, 5)

point = ajouter_point(-35.362919, 149.165452, 7)

suivre_trajectoire(vehicule, point)

voler_en_cercle(5, 3, 10)


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
