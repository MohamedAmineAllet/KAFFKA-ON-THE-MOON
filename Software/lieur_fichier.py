import subprocess

# Lancer les deux scripts en parallèle
process1 = subprocess.Popen(['python', 'main_Application.py'])
process2 = subprocess.Popen(['python', 'Hardware/main_SoftwareInTheLoop.py'])

# Attendre que les deux processus se terminent
process1.wait()
process2.wait()