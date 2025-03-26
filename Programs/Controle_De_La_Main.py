# Import the necessary Packages and scripts for this software to run (Added speak in
# there too as an Easter egg)
import cv2
from collections import Counter
from module import findnameoflandmark, findpostion, speak
import math

# Use CV2 Functionality to create a Video stream and add some values + variables
cap = cv2.VideoCapture(0)
tip=[8,12,16,20]
tipname=[8,12,16,20]
fingers=[]
finger=[]

def minimum(position, minimum):
    if position < minimum:
        return position
    else:
        return minimum
def maximum(position, maximum):
    if position > maximum:
        return position
    else:
        return maximum

# Create an infinite loop which will produce the live feed to our desktop and that will search for hands
while True:
    ret, frame = cap.read()
    flipped = cv2.flip(frame, flipCode=1)

    # Determines the frame size, 640 x 480 offers a nice balance between speed and accurate identification
    frame1 = cv2.resize(flipped, (640, 480))
     #frame1.shape[0] = 480 #donc height
     #frame1.shape[1] = 640 #donc width

    gauche = frame1.shape[1] * 0.2
    droite = frame1.shape[1] - gauche
    haut = frame1.shape[0]*0.2
    bas = frame1.shape[0] - haut


    # crée une liste des positions des jointures de chaque doigt
    a = findpostion(frame1)
    b = findnameoflandmark(frame1)

    # Below is a series of If statement that will determine if a finger is up or down and
    # then will print the details to the console
    if len(b and a) != 0:
        #initialiser les extrémités
        xMin = a[0][1]
        xMax = a[0][1]
        yMin = a[0][2]
        yMax = a[0][2]

        #trouver les extrémités de la main
        for i in range(1, len(a) - 1):
            xmin = minimum(a[i][1], xMin)
            xmax = maximum(a[i][1], xMax)
            ymin = minimum(a[i][2], yMin)
            ymax = maximum(a[i][2], yMax)


        #faire bouger selon la position dans l'écran
        if yMax > bas and yMin > haut:
            print("appeler méthode, bas")
        if yMax < bas and yMin < haut:
            print("appeler méthode, haut")
        if xMax > droite and xMin > gauche:
            print("méthode droite")
        if xMax < droite and xMin < gauche:
            print("méthode gauche")


        finger = []
        if a[0][1:] < a[4][1:]:
            finger.append(1)
        else:
            finger.append(0)

        fingers = []
        for id in range(0, 4):
            if a[tip[id]][2:] < a[tip[id] - 2][2:]:
                fingers.append(1)
            else:
                fingers.append(0)

    # Below will print to the terminal the number of fingers that are up or down
    x = fingers + finger
    c = Counter(x)
    up = c[1]

    if up == 1:
        print("avance")
    elif up == 2:
        print("recule")

    # Below shows the current frame to the desktop
    cv2.imshow("Frame", frame1);
    key = cv2.waitKey(1) & 0xFF

    # Below will speak out load when |s| is pressed on the keyboard about what fingers are up or down
    if key == ord("q"):
        break
        #speak("you have" + str(up) + "fingers up  and" + str(down) + "fingers down")
