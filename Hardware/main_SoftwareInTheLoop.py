import dronekit_sitl
from dronekit  import connect, VehicleMode
from collections.abc import MutableMapping

# Commencer SITL
sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()
vehicle = connect(connection_string, wait_ready=True) #Se connecter au véhicule simulé


print(f"Mode: {vehicle.mode.name}")

# Fermer SITL proprement
vehicle.close()
sitl.stop()