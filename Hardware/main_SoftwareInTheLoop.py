import dronekit_sitl
import time
from dronekit  import connect, VehicleMode
from collections.abc import MutableMapping

# Commencer SITL
sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()
vehicle = connect(connection_string, wait_ready=True) #Se connecter au véhicule simulé

def  arm_and_takeoff(target_altitude):
    print("Arme le drone en mode GUIDED")
    vehicle.mode = VehicleMode("GUIDED")
    while vehicle.mode.name != "GUIDED":
        time.sleep(1)

        print("Armement des moteurs...")

        vehicle.armed = True

    while not vehicle.armed:
        time.sleep(1)

    print("Décollage en cours...")
    vehicle.simple_takeoff(target_altitude)


arm_and_takeoff(10)

print("Atterrissage automatique...")
vehicle.mode = VehicleMode("LAND")


print(f"Mode: {vehicle.mode.name}")

# Fermer SITL proprement
vehicle.close()
sitl.stop()