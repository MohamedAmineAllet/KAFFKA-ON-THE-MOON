"""
Ce programme s'occupe de gerer l'image d'une caméra qui se trouve sur un drone dans ce context,il s'occupe aussi
d'afficher les commandes qui controlent le drone en question,l'application s'occupe de prendre une photo/vidéo pour la
stocker dans un fichier réservé pour ça,(...)

@autheur : Mohamed-Amine,Allet
@autheur :
@autheur :
@autheur :
@version : Python (3.11.9) Kivy(2.3.1)
"""
import os
from collections import Counter
import numpy as np
from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy.animation import Animation
from kivy.clock import Clock
import cv2
from collections import Counter
import socket
import time
import threading
import datetime
# from Hardware import main_SoftwareInTheLoop
# Biblioteque utile a la transmission video du Rpi vers l'appareil.

from pywin.framework.editor import frame

from Programs.module import findpostion, findnameoflandmark


# ********** Serveur ************* #
class serveur_application(threading.Thread):
    def __init__(self):
        super().__init__()
        self.valeur_x = 0.0  # on va changer le nom ce n'est pas que pour le
        self.valeur_y = 0.0  #
        self.valeur_z = 0.0  #
        self.running = True
        self.lock = threading.Lock()

    def run(self):
        """
        Creer un serveur pour héberger des donnéees et des informations en utilisant un socket
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server.bind(('localhost', 12345))
        server.listen(1)
        print("Serveur joystick en écoute ...")

        conn, addr = server.accept()  # addresse du client qui se connecte et socket de communication
        print("Client connecté", addr)
        while self.running:
            with self.lock:
                data = f"{self.valeur_x},{self.valeur_y}, {self.valeur_z}".encode()
            try:
                conn.sendall(data)
                time.sleep(0.05)
            except(BrokenPipeError, ConnectionResetError):
                break
        conn.close()
        server.close()

    def update_values(self, x, y, z):
        with self.lock:
            self.valeur_x = x
            self.valeur_y = y
            self.valeur_z = z



# Ici on lance le Serveur
joystick_server = serveur_application()
joystick_server.start()


# ********** Application Interface du Pilote ************* #


class JoystickDeplacementHorizental(Widget):
    """
    La class JoystickDeplacementHorizental est une classe que j'ai conçu afin de stocker deux coefficiant un en x et un en y
    que je vais utiliser pour déplacer le drone horizentalement seulement.Afin, d'illustrer ce joystick l'utilisateur
    il sera dessiner avec une premiere elipse comme background et une deuxième elipse blanche comme joystick
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (200 * (3 / 4), 200 * (3 / 4))  # Taille du joystick
        self.knob_size = (50 * (3 / 4), 50 * (3 / 4))  # Taille du bouton central
        with self.canvas:
            Color(0, 0, 1, 0.5)  # Bleu semi-transparent pour la base
            self.base = Ellipse(size=self.size, pos=self.center)  # Base fixe du joystick

            Color(1, 1, 1, 1)  # Blanc pour le bouton central
            self.knob = Ellipse(size=self.knob_size, pos=self.center)  # Bouton central
        self.bind(pos=self.update_graphics_pos)  # Met à jour les positions graphiques

    def update_graphics_pos(self, *args):
        """
        La méthode update_graphics_pos s'occupe de changer l'affichage des positions des cercles de manière interactive
        lorsque l'utilisateur clique a un endroit.
        :param self:
        :param args:
        """
        base_x = self.center_x - self.base.size[0] / 2
        base_y = self.center_y - self.base.size[1] / 2
        self.base.pos = (base_x, base_y)

        knob_x = self.center_x - self.knob.size[0] / 2
        knob_y = self.center_y - self.knob.size[1] / 2
        self.knob.pos = (knob_x, knob_y)

    def on_touch_move(self, touch):  # a ecrire toute les formules dans word.
        """
        En gros en rapide que je veux mieu écrire.(cette methode stock la valeeur de l'endroit ou touche
        l'utilisateur pour la stocker afin de l'utiliser dans l'affichage
         graphique pour aussi normalizer cette valeur afin de l'utiliser comme coefficiant x & y plus tard.
        :param touch:
        :return:
        """
        if self.disabled:
            return False
        if self.collide_point(*touch.pos):
            dx = touch.x - self.center_x  # Distance en X
            dy = touch.y - self.center_y  # Distance en Y

            # Limiter le déplacement dans un rayon maximal
            max_radius = self.size[0] / 2 - self.knob_size[0] / 2  # Rayon disponible
            distance = (dx ** 2 + dy ** 2) ** 0.5  # Distance au centre

            if distance > max_radius:
                dx = dx * max_radius / distance
                dy = dy * max_radius / distance

            knob_x = self.center_x + dx - self.knob.size[0] / 2
            knob_y = self.center_y + dy - self.knob.size[1] / 2
            self.knob.pos = (knob_x, knob_y)

            # Mettre à jour les valeurs X et Y (normalisées entre -1 et 1)
            self.value_x = dx / max_radius
            self.value_y = dy / max_radius
            # Update le transfert du coefficiant x et y.
            joystick_server.update_values(self.value_x, self.value_y, 0)  # J'ai  mis 0 comme valeur en y à envoyer

            print(f"Joystick position: X={self.value_x:.2f}, Y={self.value_y:.2f}")

    def on_touch_up(self, touch):
        if self.disabled:
            return False
        self.update_graphics_pos()

        # Envoyer les nouvelles valeurs au serveur
        def send_zero_values(dt):
            joystick_server.update_values(0.0, 0.0)
            print(f"Joystick relâché : X=0.00, Y=0.00")

        Clock.schedule_once(send_zero_values, 0.2)


class CameraWidget(Image):
    def __init__(self, **kwargs):
        super(CameraWidget, self).__init__(**kwargs)
        self.capture = None  # La capture vidéo sera activée/désactivée
        self.enregistrement_en_cours = False
        self.video_writer = None

    def demarrer_enregistrement(self, filename="VideoStockee/video.mp4", fps=15):
        if self.capture is None or not self.capture.isOpened():
            print("Erreur : La caméra n'est pas active.")
            return

        os.makedirs("VideoStockee", exist_ok=True)
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        self.recording = True
        print(f"Enregistrement démarré : {filename}")

    def stopper_enregistrement(self):
        if self.recording and self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            self.recording = False
            print("Enregistrement arrêté")

    def capture_un_frame(self):
        """
        Cette méthode me permet de capturer la frame du moment afin de l'utiliser plus tard
        dans l'Interface Pilotage.
        :return frame La frame du moment courant qui est affiché dans l'application:
        """
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret and frame is not None:
                return frame
        return None

    def start_camera(self, source=0, fps=15):
        # Demarre la camera dépendamment de la source.
        self.capture = cv2.VideoCapture(source)

        if not self.capture.isOpened():
            print("Erreur : Impossible d'ouvrir la caméra.")
            return
        Clock.schedule_interval(self.update, 1.0 / fps)

    # à changer la source pour l'URL de la caméra.
    def update(self, dt):

        if self.capture:
            ret, frame = self.capture.read()
            if ret:
                if self.enregistrement_en_cours and self.video_writer:
                    self.video_writer.write(frame)

                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.texture = texture

    def stop_camera(self):
        # Arrete la transmission video et remet l'image par defaut
        if self.capture:
            self.capture.release()
            self.capture = None
        Clock.unschedule(self.update)
        self.source = "ImageInterfaceCamera/ImageArriereFondCamera.png"


class InterfaceDAcceuil(Screen):
    pass


class InterfacePilotage(Screen):
    camera_active = False
    joystick_active = False
    drone_en_vol = False
    slider_altitude_active = False
    slider_rotation_active = False
    handtracker_active = False

    def decoller_atterir_drone(
            self):  # Pas oublier d'ajouter l'effet du drone ici en gros lorsque le drone decolle on donne une vitesse a voir avec Kemuel.
        if self.drone_en_vol:
            self.ids.img_decoller_atterir_drone.source = "ImageInterfaceCamera/ImageDecollerDrone.png"
            self.drone_en_vol = not self.drone_en_vol

            joystick_server.update_values()
        else:
            self.ids.img_decoller_atterir_drone.source = "ImageInterfaceCamera/ImageAtterireDrone.png"
            self.drone_en_vol = not self.drone_en_vol

            joystick_server.update_values()

    def demarrer_handtracking(self):
        self.handtracker_active = not self.handtracker_active;

        track = HandTracking()

        if self.handtracker_active and self.camera_active:
            self.joystick_active = False
            self.slider_altitude_active = False
            self.slider_rotation_active = False

            track.start_camera(0)
        else:
            track.stop_camera()

        # Ce code nous permet de lancer un autre fichier python dans le fichier python courrant.
        """import os
        def run_program():
            os.system('Controle_De_La_Main.py')

        if self.camera_active:
            # CODE A CHANGER TRES IMPORTANT RAISON : Dans le future parce que la camera n'est pas similaire pour les deux.
            print("Desactiver la camera")
        else:
            run_program()"""

    def connecter_la_camera(self):

        camera = self.ids.camera_widget
        if not self.camera_active:
            # Active la caméra
            camera.start_camera(0)
            self.ids.btn_activation_camera.text = "Désactiver la caméra"
        else:
            # Désactive la caméra
            camera.stop_camera()
            self.ids.btn_activation_camera.text = "Activer la caméra"
            camera.texture = Image(source="ImageInterfaceCamera/ImageArriereFondCamera.png").texture
        self.camera_active = not self.camera_active

    def afficher_les_commandes(self):
        joystick = self.ids.joystick_deplacement_horizental
        slider_altitude = self.ids.slider_altitude
        slider_rotation = self.ids.slider_rotation
        if self.joystick_active & self.slider_altitude_active & self.slider_rotation_active:
            slider_rotation.opacity = 0
            slider_rotation.disabled = True

            slider_altitude.opacity = 0
            slider_altitude.disabled = True

            joystick.opacity = 0
            joystick.disabled = True
            self.ids.btn_activation_commande.text = "Activation pilotage manuel"
        else:
            joystick.opacity = 1
            joystick.disabled = False

            slider_rotation.opacity = 1
            slider_rotation.disabled = False

            slider_altitude.opacity = 1
            slider_altitude.disabled = False
            self.ids.btn_activation_commande.text = "Desactivation pilotage manuel"
        self.slider_altitude_active = not self.slider_altitude_active
        self.slider_rotation_active = not self.slider_rotation_active
        self.joystick_active = not self.joystick_active

    def reset_slider(self):

        anim = Animation(value=0, duration=0.2)

        # Ce code anime le retour a la valeur de 0 pour le facteur de changement de vitesse d'altitude
        # et pour le facteur de changement de vitesse de rotation.

        anim.start(self.ids.slider_altitude)
        self.ids.slider_altitude.value = 0

        anim.start(self.ids.slider_rotation)
        self.ids.slider_rotation.value = 0

    def afficher_valeur(self):
        print("Valeur de la vitesse d'altitude :", self.ids.slider_altitude.value)
        print("Valeur de la vitesse de rotation :", self.ids.slider_rotation.value)

    # Bouton de droite
    def prendreUnePhoto(self):
        camera = self.ids.camera_widget
        frame = camera.capture_un_frame()

        if frame is not None:
            try:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
                nom_image = f"PhotoStockee/photo_{timestamp}.png"

                os.makedirs("PhotoStockee", exist_ok=True)
                cv2.imwrite(nom_image, frame)
                print(f"Photo sauvegardée : {nom_image}")


            except Exception as e:
                print(f"Erreur critique lors de la sauvegarde : {str(e)}")
        else:
            print("La caméra n'est pas ouverte.")

    def prendre_une_video(self):
        camera = self.ids.camera_widget
        if self.camera_active:
            if camera.enregistrement_en_cours:
                camera.stopper_enregistrement()
                camera.enregistrement_en_cours = False
                self.ids.img_prendre_video.source = "ImageInterfaceCamera/ImagePrendreVideo.png"

            else:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
                filename = f"VideoStockee/video_{timestamp}.mp4"
                camera.demarrer_enregistrement(filename)
                self.ids.img_prendre_video.source = "ImageInterfaceCamera/ImagePrendrePhoto3.png"
                camera.enregistrement_en_cours = True
        else:
            print("camera désactivée activer la pour enregistrer une vidéo")

    def reinitialization(self):
        # Reset la camera.
        camera = self.ids.camera_widget
        # Désactive la caméra
        camera.stop_camera()
        self.ids.btn_activation_camera.text = "Activer la caméra"
        camera.texture = Image(source="ImageInterfaceCamera/ImageArriereFondCamera.png").texture
        self.camera_active = not self.camera_active

        self.camera_active = not self.camera_active
        # Reset l'affichage des commandes.

        # Desactivation joystick droite
        joystick = self.ids.joystick_deplacement_horizental
        joystick.opacity = 0
        joystick.disabled = True
        self.ids.btn_activation_commande.text = "Activation pilotage manuel"
        self.joystick_active = not self.joystick_active
        # Desactivation joystick gauche
        slider_horizental = self.ids.slider_altitude
        slider_horizental.opacity = 0
        slider_horizental.disabled = True


class HandTracking(CameraWidget):
    def __init__(self, **kwargs):
        """
        constructor de la classe HandTracking
        """
        super().__init__(**kwargs)
        self.source = "0"
        self.capture = None  # La capture vidéo sera activée/désactivée

    def update(self, dt):

        self.value_x = 0
        self.value_y = 0
        self.value_z = 0

        tip = [8, 12, 16, 20]
        fingers = []
        finger = []
        if self.capture:
            ret, frame = self.capture.read()

            if ret:
                buf = cv2.flip(frame, 1).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.texture = texture
                cv2.imshow("Frame", frame)

            gauche = frame.shape[1] * 0.2
            droite = frame.shape[1] - gauche
            haut = frame.shape[0] * 0.2
            bas = frame.shape[0] - haut

            # crée une liste des positions des jointures de chaque doigt
            a = findpostion(frame)
            b = findnameoflandmark(frame)

            # Below is a series of If statement that will determine if a finger is up or down and
            # then will print the details to the console
            if len(b and a) != 0:
                # initialiser les extrémités
                x_min = a[0][1]
                x_max = a[0][1]
                y_min = a[0][2]
                y_max = a[0][2]

                # trouver les extrémités de la main
                for i in range(1, len(a) - 1):
                    x_min = min(a[i][1], x_min)
                    x_max = max(a[i][1], x_max)
                    y_min = min(a[i][2], y_min)
                    y_max = max(a[i][2], y_max)

                # faire bouger selon la position dans l'écran
                if y_max > bas and y_min > haut:
                    print("méthode BAS")
                    self.value_z = -1
                if y_max < bas and y_min < haut:
                    print("méthode HAUT")
                    self.value_z = 1
                if x_max > droite and x_min > gauche:
                    print("méthode DROITE")
                    self.value_y = 1
                if x_max < droite and x_min < gauche:
                    print("méthode GAUCHE")
                    self.value_y = -1

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

        x = fingers + finger
        c = Counter(x)
        up = c[1]

        if up == 2:
            print("avance")
            self.value_x = 1
        elif up == 3:
            print("recule")
            self.value_x = -1

        joystick_server.update_values(self.value_x, self.value_y, self.value_z)

        key = cv2.waitKey(1) & 0xFF
        # Below will speak out load when |s| is pressed on the keyboard about what fingers are up or down
        if key == ord("q"):
            self.stop_camera()

# case no hand: values set to 0
# quand ferme handtracking, revient cam normale

class CameraProjetApp(App):
    def build(self):
        sm = ScreenManager()
        # Permet de choisir le type de transition.
        sm.transition = RiseInTransition()
        return sm


if __name__ == '__main__':
    CameraProjetApp().run()
