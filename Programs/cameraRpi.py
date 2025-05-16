import cv2
import time

# 🔁 Essaie d'ouvrir la source vidéo jusqu'à ce que ça marche
def attendre_flux(source):
    cap = cv2.VideoCapture(source, cv2.CAP_GSTREAMER)
    retry_count = 0

    while not cap.isOpened():
        print(f"🕓 En attente du flux vidéo... Tentative {retry_count+1}")
        time.sleep(1)
        cap = cv2.VideoCapture(source, cv2.CAP_GSTREAMER)
        retry_count += 1
        if retry_count > 10:
            print("❌ Impossible de recevoir le flux. Abandon.")
            return None
    return cap

# 🎯 Adresse de réception UDP (ajuste le port si nécessaire)
udp_source = 'udp://0.0.0.0:5000'

# 📥 Attente du flux
cap = attendre_flux(udp_source)

if cap is None:
    exit(1)

print("✅ Flux reçu ! Affichage en cours...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame non reçue correctement.")
        continue

    cv2.imshow("🎥 Flux Vidéo (PC)", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # touche ÉCHAP pour quitter
        print("👋 Fin du programme.")
        break

cap.release()
cv2.destroyAllWindows()
