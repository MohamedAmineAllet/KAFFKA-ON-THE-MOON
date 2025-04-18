import cv2
from matplotlib import pyplot as plt

print("salut")
cap = cv2.VideoCapture(2)
ret, frame = cap.read()
plt.imshow(frame)

if cap.isOpened():
    print("✅ Caméra index 0 ouverte")
else:
    print("❌ Aucune caméra à l'index 0")
cap.release()

