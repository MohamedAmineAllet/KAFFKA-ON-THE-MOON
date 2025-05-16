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

print("Tous le monde est prêt? On met les voiiiles...")

# Commencer la simulation
sitl = dronekit_sitl.start_default()
connection_string = 'tcp:127.0.0.1:5760'  # Port ouvert par SITL

print(f"La chaîne de connection du véhicule: {connection_string}")
# Se connecter au véhicule simulé
vehicule = connect(connection_string, wait_ready=True)


def setMode(modeNumber):
    """
    Forcer le mode guide via mavlink
    :type modeId: code mavlink pour le mode
    Mode	custom_mode (MAVLink)
    STABILIZE   	0
    ACRO	        1
    ALT_HOLD    	2
    AUTO	        3
    GUIDED	        4
    LOITER	        5
    RTL         	6
    CIRCLE	        7
    LAND	        9
    DRIFT	        11
    SPORT	        13
    POSHOLD     	16
    BRAKE	        17
    THROW	        18
    AVOID_ADSB	    19
    GUIDED_NO_GPS	20
    """
    vehicule._master.mav.set_mode_send(
        vehicule._master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        modeNumber
    )
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


# Stockage de la position initiale
position_initiale = None


def setVitesse(vx, vy, vz, vsintheta, duree):
    """
    Déplacer notre véhicule dans une certaine direction en changeant le vecteur vitesse
    :param vx: + Nord / - Sud      ||  + Devant / - Derrière
    :param vy: + Est / - Ouest     || + Droite / - Gauche
    :param vz: + Bas / - Haut      || + Bas / - Haut
    Système de coordonnées conventionel NED  ||  Système de coordonnées Relatve au drone <-
    """
    global position_initiale

    # Capturer la position initiale au premier appel
    if position_initiale is None:
        position_initiale = vehicule.location.local_frame  # NED par rapport à home

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
        """ # Afficher la position relative au vehicule
        position_ned = vehicule.location.local_frame  # [North, East, Down] en mètres
        yaw = vehicule.attitude.yaw  # Orientation du drone (yaw) en radians
        latitude = vehicule.location.global_frame.lat  # Current latitude
        longitude = vehicule.location.global_frame.lon  # Current longitude
        altitude = vehicule.location.global_relative_frame.alt  # Altitude
        # print(" latitude : %.6f" % latitude + " longitude : %.6f" % longitude + " altidude: %.2f m" % altitude)
        print(f"Vitesse actuelle: Vx={vx:.2f}, Vy={vy:.2f}, Vz={vz:.2f}")"""
        # Position actuelle
        position_actuelle = vehicule.location.local_frame  # [North, East, Down]

        # Calcul du déplacement par rapport à la position initiale
        if position_actuelle and position_initiale:
            delta_x = position_actuelle.north - position_initiale.north
            delta_y = position_actuelle.east - position_initiale.east
            delta_z = position_actuelle.down - position_initiale.down  # Z négatif vers le bas

            print(f"Déplacement relatif: ΔX={delta_x:.2f}m, ΔY={delta_y:.2f}m, ΔZ={delta_z:.2f}m")
            print(f"Vitesse actuelle: Vx={vx:.2f}, Vy={vy:.2f}, Vz={vz:.2f}")


def arm_and_takeoff(target_altitude):
    """
    Méthode pour armer et faire décoller à une altitude donnée
    :param target_altitude:
    :return: a ready to fly copter
    """
    while not vehicule.is_armable:
        print("wait for vehicle to be armed")
        time.sleep(1)

    # Changer le mode du drone en "GUIDED"
    while vehicule.mode.name != 'GUIDED':
        print("- En attente du changement de mode en GUIDED...")
        setMode(4)  # Mode GUIDED = 4 en ArduPilot
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
        print("Altitude Actuelle: %d" % vehicule.location.global_relative_frame.alt)
        if vehicule.location.global_relative_frame.alt > target_altitude:
            break
        time.sleep(1)
    print("Target altitude reached")
    return None


def ajouter_point(latitude, longitude, altitude):
    return LocationGlobalRelative(latitude, longitude, altitude)


def suivre_trajectoire(vehicule, point, vitesse=10):
    """
    simple goto mais en affichant la distance restante.
    IMPORTANT: ici on travail avec des location.global_relative_frame
    soit des altitudes et des longitudes qui suivent les coordonées WGS84 (gps)
    :param vehicule:
    :param point:
    :param vitesse:
    """
    print(f"Navigation vers {point.lat}, {point.lon}, {point.alt}m")

    vehicule.simple_goto(point, groundspeed=vitesse)

    while True:  # permet de calculer la distance restante jusqu'a notre point
        position_actuelle = vehicule.location.global_relative_frame
        distance = math.sqrt(
            (point.lat - position_actuelle.lat) ** 2 +
            (point.lon - position_actuelle.lon) ** 2
        ) * 111320  # Convertir degrés en mètres, 1 degres = 111320m

        print(f" Distance restante : {distance:.2f}m")
        if distance < 2:
            print("trajectoire atteinte !")
            break
        time.sleep(2)


def voler_en_cercle(vitesse, boucles, duree):
    """
    faire voler le drone en cercle.
    PS: J'aimerais aussi faire un tourbillon plus tard!!!
    ** si je dis pas de la merde pour les paramètres **
    :param vitesse: pour chaque "points"
    :param boucles: nombre de tours
    :param duree: temps pour chaque points
    """
    print("demarrage du vol en cercle")
    points = 36  # nombre de points selon la grandeur du cercle
    angle_step = 2 * math.pi / points
    for loop in range(0, boucles):
        for point in range(points):
            angle = point * angle_step
            vx = vitesse * math.cos(angle)  # Vitesse sur l'axe Nord/Sud
            vy = vitesse * math.sin(angle)  # Vitesse sur l'axe Est/Ouest
            vz = 0  # Altitude constante
            setVitesse(vx, vy, vz, duree)  # effets de la durée sur le cercle???

    print("vole en cercle terminer")
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


def atterisage_du_drone():
    setMode(9)
    while True:  # le drone déscend dans l'axe z, mais on aime pas le produit vectoriel
        altitude = vehicule.location.global_relative_frame.alt
        print(f"Altitude actuelle : {altitude:.2f} m")
        time.sleep(1)
        # son altitude diminiue jusqu'à tant qu'il arrive à 0.1 (pour éviter tout problème)
        if altitude <= 0.1:
            print("Le sol a été atteint, on desarme")
            vehicule.armed = False
            break
    print("Drone désarmé, atterrissage terminé.")


def client_du_joystick():
    """
    Utilisation de socket (Interface de connection réseau) pour se connecter en tant que client
    au serveur de l'application et recevoir des valeurs et informations ex: joystick
    """
    while True:  # boucle infinie pour se connecter au serveur et gérer les données en continu
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 , TCP
            client.connect(("localhost", 12345))
            print("Connecté au serveur joystick")

            while True:
                data = client.recv(
                    1024).decode()  # Décoder les informations venant du serveur (dans l'application)
                if not data:  # pas de message => break
                    setMode(5)  # on ne bouge pas mode loiter
                    break
                try:
                    x_str, y_str, z_str, cos_theta_str = data.split(
                        ',')  # valeurs selon l'axe des x et y dans un plan parallèle au sol entre [-1, 1]
                    Vy = float(x_str) * 20  # pour nous y c'est l'axe est ouest donc x du joystick
                    Vx = float(y_str) * 20  # Pour nous x c'est l'axe nord sud donc y du joystick
                    Vz = float(z_str) * 20  # Pour nous x c'est l'axe nord sud donc y du joystick
                    Vtheta = float(cos_theta_str) * 20
                    setVitesse(Vx, Vy, Vz, Vtheta, 5)
                    print(f" Vx : {Vx:.2f} m", f" Vy : {Vy:.2f} m", f" Vz : {Vz:.2f} m")

                except ValueError:
                    print("Données invalides :", data)
        except(ConnectionRefusedError, ConnectionResetError) as e:  # erreurs de connections
            print("Erreur de connection...")
            time.sleep(1)
        finally:
            client.close()


# Crée un thread pour excécuter la fonction client en arrière plan
# joystick_thread = threading.Thread(target=client_du_joystick, daemon=True)
# joystick_thread.start()

""" ******* La Mission en question ****** """
# vehicle = connectMyCopter() # Pour le Speedou
arm_and_takeoff(4)
while True:
    client_du_joystick()

    """ 
    # vers le Nord
    setVitesse(10, 0, 0, 10)
    
    # vers le Sud
    setVitesse(-10, 0, 0, 10)
    
    # ne pas bouger durant 5s
    setMode(5)  # Loiter
    time.sleep(5)
    setMode(4)
    
    # vers l'Est
    setVitesse(0, 10, 0, 10)
    
    # vers l'Ouest
    setVitesse(0, -10, 0, 10)
    
    # se rendre à un point précis
    point = ajouter_point(-35.362919, 149.165452, 7)
    suivre_trajectoire(vehicule, point)
    
    # titre assez explicite
    voler_en_cercle(5, 1, 1)
    
    # setMode(6) # Mode RTL = 6 en ArduPilot
    
    # Le drone atterit!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    atterisage_du_drone()
    time.sleep(30)
    """

# Fermer SITL proprement
time.sleep(2)
vehicule.close()
sitl.stop()

###### problèmes ######
# - Faire un tourbillon
# - le code du cercle
# -
