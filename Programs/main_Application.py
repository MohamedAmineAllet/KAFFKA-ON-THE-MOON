"""
Ce programme s'occupe de gerer l'image d'une caméra qui se trouve sur un drone dans ce context,il s'occupe aussi
d'afficher les commandes qui controlent le drone en question,l'application s'occupe de prendre une photo/vidéo pour la
stocker dans un fichier réservé pour ça,(...)

@autheur : Mohamed-Amine,Allet
@autheur :Gokhale,Kian
@autheur :
@autheur :
@version : Python (3.11.9) Kivy(2.3.1)
"""
import os
from collections import Counter

import numpy as np
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
import cv2
from collections import Counter
import socket
import time
import threading
import datetime

from numpy.core.defchararray import center
# from Hardware import main_SoftwareInTheLoop
# Biblioteque utile a la transmission video du Rpi vers l'appareil.

from pywin.framework.editor import frame

from Programs.module import findpostion, findnameoflandmark


# ********** SERVEUR ********** #
class ServeurApplication(threading.Thread):
    def __init__(self):
        """
        Self est un objet courant de CETTE classe
        On initialise ici avec des valeurs qui nous seront utiles pour le manimant du drone.
        """
        super().__init__()
        self.valeur_x = 0.0
        self.valeur_y = 0.0
        self.valeur_z = 0.0
        self.valeur_cos_theta = 0.0
        self.running = True
        self.lock = threading.Lock()

    def run(self):
        """
        Creer un serveur pour héberger et envoyer des donnéees et des informations en utilisant une socket
        """
        serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Protocole utilisé TCP

        HOST = ''
        PORT = 12345

        serveur.bind((HOST, PORT))
        serveur.listen(1)
        print("Serveur Application en écoute ...")

        conn, addr = serveur.accept()  # addresse du client qui se connecte et socket de communication
        print("Client connecté", addr)

        while self.running:
            with self.lock:
                data = f"{self.valeur_x},{self.valeur_y}, {self.valeur_z},{self.valeur_cos_theta}".encode()
            try:
                conn.sendall(data)
                time.sleep(0.05)
            except(BrokenPipeError, ConnectionResetError):
                break
        conn.close()
        serveur.close()

    def update_values(self, x, y, z, cos_theta):
        """
        methode pour envoyer des valeurs de directions via le serveur depuis les autres méthodes
        IMPORTANT: On se base sur le joystick pour les valeurs à envoyer.
        Ses valeurs seront ajustées dans SITL
        :param x: axe gauche droite (joystick et handtracking)
        :param y: axe devant derrière (joystick et handtracking)
        :param z: paramètre pour monter et descendre
        :param cos_theta: paramètre pour faire rotationner le drone sur lui même.
        :return: none (la fonction change les paramètre de self)
        """
        with self.lock:
            self.valeur_x = x
            self.valeur_y = y
            self.valeur_z = z
            self.valeur_cos_theta = cos_theta


# Ici on lance le Serveur
joystick_server = ServeurApplication()
joystick_server.start()


# ********** Application Interface du Pilote ************* #

class JoystickDeplacementHorizental(Widget):
    """
    La class JoystickDeplacementHorizental est une classe que j'ai conçu afin de stocker deux coefficiant un en x et un en y
    que je vais utiliser pour déplacer le drone horizentalement seulement.Afin, d'illustrer ce joystick à l'utilisateur
    il sera dessiner avec une premiere elipse comme background et une deuxième elipse blanche comme joystick
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (200 * (3 / 4), 200 * (3 / 4))
        self.knob_size = (50 * (3 / 4), 50 * (3 / 4))
        with self.canvas:
            Color(0, 0, 1, 0.5)
            self.base = Ellipse(size=self.size, pos=self.center)

            Color(1, 1, 1, 1)
            self.knob = Ellipse(size=self.knob_size, pos=self.center)
        self.bind(pos=self.update_graphics_pos)  # Met à jour les positions graphiques

    def update_graphics_pos(self, *args):
        """
        La méthode update_graphics_pos s'occupe de changer l'affichage des positions des cercles de manière interactive
        lorsque l'utilisateur clique à un endroit l'élipse blanche se dessine à l'endroit où se trouve la souris/le doight.
        """
        base_x = self.center_x - self.base.size[0] / 2
        base_y = self.center_y - self.base.size[1] / 2
        self.base.pos = (base_x, base_y)

        knob_x = self.center_x - self.knob.size[0] / 2
        knob_y = self.center_y - self.knob.size[1] / 2
        self.knob.pos = (knob_x, knob_y)

    def on_touch_move(self, touch):  # a ecrire toute les formules dans word.
        """
        Cette méthode permet que lorsque l'utilisateur clique a un endroit dans le cercle bleu une
        valeur en x et y sont stocké qui dépende de la distance entre le centre du cercle bleue
        et l'endroit appuyée.Afin de limiter cette valeur on la normalise pour obtenir une valeur
        entre -1 et 1 qui va servir de coéfficiant de variation de vitesse.Pour ensuite,envoyer cette valeur par
        notre serveur socket dans l'autre main(main_SoftwareInTheLoop.py)
        :param touch:
        :return:
        """
        if self.disabled:
            return False
        if self.collide_point(*touch.pos):
            dx = touch.x - self.center_x  # Distance en X
            dy = touch.y - self.center_y  # Distance en Y

            # Limiter le déplacement dans un rayon maximal
            max_radius = self.size[0] / 2 - self.knob_size[0] / 2
            distance = (dx ** 2 + dy ** 2) ** 0.5  # Distance au centre

            if distance > max_radius:
                dx = dx * max_radius / distance
                dy = dy * max_radius / distance

            knob_x = self.center_x + dx - self.knob.size[0] / 2
            knob_y = self.center_y + dy - self.knob.size[1] / 2
            self.knob.pos = (knob_x, knob_y)

            # Mets à jour les valeurs X et Y (normalisées entre -1 et 1)
            self.value_x = dx / max_radius
            self.value_y = dy / max_radius
            # Update le transfert du coefficiant x et y.
            joystick_server.update_values(self.value_x, self.value_y, 0, 0)  # z en z c'est un espace R2

            print(f"Joystick position: X={self.value_x:.2f}, Y={self.value_y:.2f}")

    def on_touch_up(self, touch):
        if self.disabled:
            return False
        self.update_graphics_pos()


        def send_zero_values(dt):
            """
            Lorsque l'utilisateur relache le joystick ,afin que le drone ne bouge pas en
            permanance sans qu'on lui donne d'ordre,les valeurs des différents coefficiant
            de variation de vitesse sont renitializer a 0 pour que le drone devient stable.
            :rtype: object
            """
            joystick_server.update_values(0.0, 0.0, 0, 0)
            print(f"Joystick relâché : X=0.00, Y=0.00, Z=0.00,cos_theta=0.00")

        Clock.schedule_once(send_zero_values, 0.2)


class CameraWidget(Image):
    """
    Cette objet est un Widget qui a pour fonction principale de permettre à l'utilisateur du drone de voir les images que
    film la caméra(le IMX219) sur le drone par l'affichage de celle-ci dans l'application kivy.
    """
    def __init__(self, **kwargs):
        super(CameraWidget, self).__init__(**kwargs)
        self.capture = None  # La capture vidéo sera activée/désactivée
        self.enregistrement_en_cours = False
        self.video_writer = None

    def demarrer_enregistrement(self, filename="VideoStockee/video.mp4", fps=15):
        """
        Cette fonction va être utile pour le bouton s'occupant de filmer une vidéo.Sachant que l'affichage
        visuelle est déjà lancé elle permet de prendre une certaine partie de cette affichage lorsqu'on clique sur
        le bouton en question et de le stocker dans le fichier VideoStockee et dans le cas ou il n'est pas présent
        il va le créer.
        :param filename: est le chemin du dossier où sont stocké les vidéoes.
        :param fps: est la constante qu'on assigne pour l'affichage de la vidéo.
        :return:
        """
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
        else:
            print("La frame n'existe pas dans le programme")

        return None

    def start_camera(self, source=0, fps=60):
        # Demarre la camera dépendamment de la source.
        print("ouvrir caméra ça peut prendre du temps")
        self.capture = cv2.VideoCapture('udp://@0.0.0.0:5000', cv2.CAP_FFMPEG)

        if not self.capture.isOpened():
            print("Erreur : Impossible d'ouvrir la caméra.")
            self.capture.release()
            cv2.destroyAllWindows()
            return
        Clock.schedule_interval(self.update, 1.0 / fps)

    # à changer la source pour l'URL de la caméra.
    def update(self, dt):
        """
        Met à jour l'image de la caméra et l'affiche dans l'interface Kivy.

        Cette méthode est appelée à chaque intervalle de temps défini (dt).
        Elle lit une nouvelle image depuis la capture vidéo en cours, l'enregistre
        si l'enregistrement est activé, et met à jour la texture affichée dans l'interface Kivy.

        :param dt: est le temps écoulé depuis le dernier appel de cette méthode, en secondes.
        """
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
    def __init__(self, **kwargs):
        super(InterfacePilotage, self).__init__(**kwargs)
        self.hand_tracker = None
        self.camera_active = False
        self.joystick_active = False
        self.drone_en_vol = False
        self.slider_altitude_active = False
        self.slider_rotation_active = False
        self.handtracking_active = False
        self.camera_est_image_principal = True
        # Planifie la mise à jour du handtracking
        Clock.schedule_interval(self.update_handtracking, 1.0 / 30.0)  # 30 FPS

    def decoller_atterir_drone(
            self):  # Pas oublier d'ajouter l'effet du drone ici en gros lorsque le drone decolle on donne une vitesse a voir avec Kemuel.
        if self.drone_en_vol:
            self.ids.img_decoller_atterir_drone.source = "ImageInterfaceCamera/ImageDecollerDrone.png"
            self.drone_en_vol = not self.drone_en_vol

            #joystick_server.update_values()
        else:
            self.ids.img_decoller_atterir_drone.source = "ImageInterfaceCamera/ImageAtterireDrone.png"
            self.drone_en_vol = not self.drone_en_vol

            #joystick_server.update_values()

    def update_handtracking(self, dt):
        if self.handtracking_active and self.hand_tracker:
            texture = self.hand_tracker.update()
            if texture:
                self.ids.handtracking_image.texture = texture

    def demarrer_handtracking(self):
        if not self.handtracking_active:
            self.hand_tracker = HandTracking(source=0)
            Clock.schedule_interval(self.hand_tracker.update, 1.0 / 30.0)  # Planifiez l'update
            self.handtracking_active = True
            self.ids.handtracking_image.opacity = 1
        else:
            if self.hand_tracker:
                Clock.unschedule(self.hand_tracker.update)
                self.hand_tracker.stop()
            self.handtracking_active = False
            self.ids.handtracking_image.opacity = 0

    def detection_plante(self):
        print("detection plante pas encore codée")

    def connecter_la_camera(self):

        camera = self.ids.camera_widget
        if not self.camera_active:
            # Active la caméra
            camera.start_camera(1)
            self.ids.btn_activation_camera.text = "Désactiver la caméra"
        else:
            # Désactive la caméra
            camera.stop_camera()
            self.ids.btn_activation_camera.text = "Activer la caméra"
            camera.texture = Image(source="ImageInterfaceCamera/ImageArriereFondCamera.png").texture
        self.camera_active = not self.camera_active

    def afficher_les_commandes(self):
        """
        Cette méthode fait en sorte que lorsqu'on clique sur le bouton avec écrit "ACTIVATION PILOTAGE MANUEL"
        les commandes s'affiche et l'utilisateur peut modifier les valeurs transmisse au drone.

        Ensuite le bouton change pour devenir un bouton avec écrit "DÉSACTIVATION PILOTAGE MANUEL" et lorsque
        l'utilisateur clique dessus l'affichage des commandes disparait et l'utilisateur ne peut plus faire bouger
        le drone par les commandes jusqu'a ce qu'il clique sur le bouton a nouveau.
        """
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
        """
        Afin d'éviter que le drone reste en mouvement même lorsqu'on ne désire pas le faire bouger si l'utilisateur
        relache les sliders alors sa valeur revient a 0 qui veut juste dire que le drone n'a plus de vitesse en altitude
        et en rotation sur lui-même.
        """
        anim = Animation(value=0, duration=0.2)

        # Ce code anime le retour a la valeur de 0 pour le facteur de changement de vitesse d'altitude
        # et pour le facteur de changement de vitesse de rotation.

        anim.start(self.ids.slider_altitude)
        self.ids.slider_altitude.value = 0

        anim.start(self.ids.slider_rotation)
        self.ids.slider_rotation.value = 0

    # Bouton de droite
    def echanger_dimension_camera(self):
        """
        Cette méthode permet d'échanger la position de l’image illustrant les deux caméras,
        les dimensions des l’images illustrant les caméras et
        d'interchanger leur positionnement en tant que Widget dans le root. (si on ne change pas ça l’image en haut à droite
        serait camouflé derrière l’autre caméra. Ici qui est le paysage d’un coucher de soleil.)
        Par deux caméras je parle des deux suivantes :
        - Celle implanté dans l’appareil qui fait tourner l’application qu’on accède dans le code par cv2.VideoCapture(0) // 0 pour la caméra par défaut dans l’appareil.
        - Celle que nous avons mis dans le drone soit le modèle IMX219//  qu’on accède avec le code suivant : cv2.VideoCapture('udp://@0.0.0.0:5000', cv2.CAP_FFMPEG)
        :return:
        """
        camera_principale = self.ids.camera_widget
        camera_handtracking = self.ids.handtracking_image
        parent = camera_principale.parent

        if not parent:
            return


        parent.remove_widget(camera_principale)
        parent.remove_widget(camera_handtracking)

        if self.camera_est_image_principal:

            camera_principale.size_hint = (0.25, 0.25)
            camera_principale.pos_hint = {"center_x": 0.75, "center_y": 0.85}


            camera_handtracking.size_hint = (1, 1)
            camera_handtracking.pos_hint = {"center_x": 0.5, "center_y": 0.5}


            parent.add_widget(camera_handtracking)
            parent.add_widget(camera_principale)

        else:

            camera_handtracking.size_hint = (0.25, 0.25)
            camera_handtracking.pos_hint = {"center_x": 0.75, "center_y": 0.85}


            camera_principale.size_hint = (1, 1)
            camera_principale.pos_hint = {"center_x": 0.5, "center_y": 0.5}


            parent.add_widget(camera_principale)
            parent.add_widget(camera_handtracking)


        self.camera_est_image_principal = not self.camera_est_image_principal

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
                self.ids.img_prendre_video.source = "ImageInterfaceCamera/ImageArreterVideo.png"
                camera.enregistrement_en_cours = True
        else:
            print("camera désactivée activer la pour enregistrer une vidéo")

    def reinitialization(self):
        """
        Cette fonction fait en sorte que lorsque l'utilisateur quitte d'interface tout est reset la caméra
        ne reste pas allumé les joysticks se mettent en mode désactiver et les sliders.
        """
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

        slider_vertical = self.ids.slider_rotation
        slider_vertical.opacity = 0
        slider_vertical.disabled = True


# *********** GALERIE PHOTO ************ #

class InterfaceGaleriePhoto(Screen):
    class InterfaceGaleriePhoto(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.boutons = []
            self.dossier_path = "PhotoStockee"

        def on_pre_enter(self):
            self.creer_liste_fichiers_images()
            self.creer_boutons()

        def creer_liste_fichiers_images(self):
            self.liste_fichiers_images = []
            for file in os.listdir(self.dossier_path):
                if file.endswith(".png"):
                    self.liste_fichiers_images.append(file)
                    print(f"Image ajoutée : {file}")

        def creer_boutons(self):
            self.ids.grid.clear_widgets()

            for image in self.liste_fichiers_images:
                image_path = os.path.join(self.dossier_path, image)
                bouton = Button(
                    background_normal=image_path,
                    size_hint=(0.8, 0.8)
                )
                bouton.bind(on_press=lambda instance, img=image_path: self.afficher_images(img))
                self.ids.grid.add_widget(bouton)

        def afficher_images(self, image):
            print("Afficher images")


# *********** HANDTRACKING ************* #
class HandTracking:
    def __init__(self, source=0):
        """
        constructeur de la classe HandTracking
        """
        self.source = "0"
        self.capture = cv2.VideoCapture(source)
        self.value_x = 0
        self.value_y = 0
        self.value_z = 0
        self.texture = None

    def update(self, dt=None):
        ret, frame = self.capture.read()
        if not ret:
            return None
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        tip = [8, 12, 16, 20]
        fingers = []

        finger = []
        self.value_x = 0
        self.value_y = 0
        self.value_z = 0

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

            # déterminer la commande selon la position dans l'écran
            if y_max > bas and y_min > haut:
                # print("méthode BAS")
                self.value_z = 1  # l'axe z dans sitl pointe vers le bas
            if y_max < bas and y_min < haut:
                # print("méthode HAUT")
                self.value_z = -1
            if x_max > droite and x_min > gauche:
                # print("méthode DROITE")
                self.value_x = 1  # conformément au joystick l'axe x est droite-gauche
            if x_max < droite and x_min < gauche:
                # print("méthode GAUCHE")
                self.value_x = -1

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
            # conformément au joystick l'axe y est devant-derrière
            self.value_y = 1
        elif up == 3:
            self.value_y = -1
        joystick_server.update_values(self.value_x, self.value_y, self.value_z, 0)

        buf = cv2.flip(frame, 0).tobytes()
        self.texture = Texture.create(size=(w, h), colorfmt='bgr')
        self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        return self.texture


    def stop(self):
        if self.capture:
            self.capture.release()


# case no hand: values set to 0
# quand ferme handtracking, revient cam normale

class CameraProjetApp(App):
    def build(self):
        self.icon = "ImageIcons/ImageRevelationDesOuvriersDurantCetteSession.jpeg"
        sm = ScreenManager()
        # Permet de choisir le type de transition.
        sm.transition = RiseInTransition()
        return sm


# *********** ON LANCE L'APPLICATION *********** #
if __name__ == '__main__':
    CameraProjetApp().run()
