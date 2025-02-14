import dronekit_sitl
import time
import argparse
import subprocess
from dronekit import connect, VehicleMode

# Tentative de connexion avec mission planner
print("MavProxy Port set!")

# Chemin vers MAVProxy, à ajuster selon ton installation
mavproxy_path = "C:\\Users\\nadau\\AppData\\Local\\Programs\\Python\\Python312\\Scripts\\mavproxy.py"

# Lancer MAVProxy en arrière-plan avec les arguments appropriés
subprocess.Popen([
    "python",  # Assure-toi d'utiliser le bon interpréteur Python
    mavproxy_path,
    "--master=tcp:127.0.0.1:5760",
    "--sitl=127.0.0.1:5501",
    "--out=127.0.0.1:14552"
])

# Démarrer SITL
sitl = dronekit_sitl.start_default()
# connection_string = sitl.connection_string()  # Par défaut, utiliser SITL local
vehicle = None


def connectMyCopter():
    parser = argparse.ArgumentParser(description="commands")
    parser.add_argument("--connect", help="Connection string to vehicle (e.g., tcp:127.0.0.1:5760)")
    args = parser.parse_args()
    connection_string = args.connect if args.connect else sitl.connection_string()

    print(f"Connecting to vehicle on: {connection_string}")
    return connect(connection_string, wait_ready=True)


def arm_and_takeoff(target_altitude):
    print("Waiting for vehicle to be armable...")
    while not vehicle.is_armable:
        time.sleep(1)

    print("Arming motors...")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(target_altitude)

    while True:
        print(f"Current Altitude: {vehicle.location.global_relative_frame.alt:.1f}")
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Target altitude reached")
            break
        time.sleep(1)


vehicle = connectMyCopter()
arm_and_takeoff(2)

print("Landing...")
vehicle.mode = VehicleMode("LAND")
time.sleep(10)

print("Closing vehicle connection...")
vehicle.close()

# Fermer SITL proprement
sitl.stop()
print("SITL stopped")

# print ("Start simulator (SITL)")
# import dronekit_sitl
# sitl = dronekit_sitl.start_default()
# connection_string = sitl.connection_string()
#
# # Import DroneKit-Python
# from dronekit import connect, VehicleMode
#
# # Connect to the Vehicle.
# print("Connecting to vehicle on: %s" % (connection_string,))
# vehicle = connect(connection_string, wait_ready=True)
#
# # Get some vehicle attributes (state)
# print ("Get some vehicle attribute values:")
# print (" GPS: %s" % vehicle.gps_0)
# print (" Battery: %s" % vehicle.battery)
# print (" Last Heartbeat: %s" % vehicle.last_heartbeat)
# print (" Is Armable?: %s" % vehicle.is_armable)
# print (" System status: %s" % vehicle.system_status.state)
# print (" Mode: %s" % vehicle.mode.name)    # settable
#
# # Close vehicle object before exiting script
# vehicle.close()
#
# # Shut down simulator
# sitl.stop()
# print("Completed")
