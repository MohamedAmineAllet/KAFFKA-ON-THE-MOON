import cv2

# Ouvre la capture en réseau
cap = cv2.VideoCapture('udp://@0.0.0.0:5000', cv2.CAP_FFMPEG)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Pas d'image reçue")
        break

    cv2.imshow('Flux RPi', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
