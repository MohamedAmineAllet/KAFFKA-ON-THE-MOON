# relieur.py
import time
import subprocess

# Démarrer d'abord le serveur (main_Application)
process1 = subprocess.Popen(['python', 'main_Application.py'])
time.sleep(2)  # Laisser le temps au serveur de démarrer

# Démarrer ensuite le client (main_SoftwareInTheLoop)
process2 = subprocess.Popen(['python', 'Hardware/main_SoftwareInTheLoop.py'])

process1.wait()
process2.wait()