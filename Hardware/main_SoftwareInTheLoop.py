import dronekit_sitl
import time
import argparse

import collections

from dronekit_sitl.pysim.sim_wrapper import counter

if not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping


from dronekit import connect, VehicleMode
from pymavlink import mavutil

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

def set_velocity_body(vx, vy, vz):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,
        0,0,
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
        0B0000111111000111,
        vx,vy,vz,
        0,0,0,
        0,0,)
    vehicle.send_mavlink(msg)
    vehicle.flush()


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
arm_and_takeoff(4)
counter = 0
while counter < 2:
    set_velocity_body(1, 0, 0)
    print("direction Nord")
    time.sleep(1)
    counter = counter + 1
#negative sud, positif nord
time.sleep(1)
counter = 0

while counter < 2:
    set_velocity_body(-1, 0, 0)
    print("direction Sud")
    time.sleep(1)
    counter = counter + 1

time.sleep(1)
counter = 0
#negative ouest, positif est
while counter < 2:
    set_velocity_body(0, 1, 0)
    print("direction est")
    time.sleep(1)
    counter = counter + 1

time.sleep(1)
counter = 0

while counter < 2:
    set_velocity_body(0, -1, 0)
    print("direction ouest")
    time.sleep(1)
    counter = counter + 1

time.sleep(1)
counter = 0

vehicle.mode = VehicleMode("RTL")
#retourne au lauch






#vehicle.mode = VehicleMode("LAND")
time.sleep(2)

while True:
    time.sleep(2)

vehicle.close()
sitl.stop()
#print(f"Mode: {vehicle.mode.name}")

# Fermer SITL proprement


