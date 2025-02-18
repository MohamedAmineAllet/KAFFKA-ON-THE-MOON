import dronekit_sitl
import time
import argparse

import collections
if not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping


from dronekit import connect, VehicleMode

# Commencer SITL
sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()

print(f"Connect Mission Planner to: {connection_string}")  # Print the connection strin
vehicle = connect(connection_string, wait_ready=True)  # Se connecter au véhicule simulé


def connectMyCopter():
    parser = argparse.ArgumentParser(description="commands")
    parser.add_argument("--connect", default=connection_string)
    args = parser.parse_args()
    vehicle = connect(connection_string, wait_ready=True)
    return vehicle


def arm_and_takeoff(target_altitude):
    while not vehicle.is_armable:
        print("wait for vehicle to be armed")
        time.sleep(1)

    vehicle.mode = VehicleMode("GUIDED")
    while vehicle.mode.name != "GUIDED":
        time.sleep(1)

        vehicle.armed = True

    while not vehicle.armed:
        time.sleep(1)

    vehicle.simple_takeoff(target_altitude)

    while True:
        print("Current Altitude: %d" % vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt > target_altitude:
            break
        time.sleep(1)
    print("Target altitude reached")
    return None


vehicle = connectMyCopter()
vehicle.mode = VehicleMode("GUIDED")
arm_and_takeoff(2)
vehicle.mode = VehicleMode("LAND")
time.sleep(2)

while True:
    time.sleep(2)

vehicle.close()
sitl.stop()
#print(f"Mode: {vehicle.mode.name}")

# Fermer SITL proprement


