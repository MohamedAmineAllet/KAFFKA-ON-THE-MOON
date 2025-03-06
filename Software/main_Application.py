from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition, FadeTransition, RiseInTransition, \
    SwapTransition
import cv2
#Biblioteque utile a la transmission video du Rpy vers l'appareil.


class CameraWidget(Image):
    def __init__(self, **kwargs):
        super(CameraWidget, self).__init__(**kwargs)
        self.capture = None  # La capture vidéo sera activée/désactivée

#a changer la source pour l'URL de la camera.
    def start_camera(self,source=0, fps=30):
        #Demarre la camera dependamment de la source.
        self.capture = cv2.VideoCapture(source)

        if not self.capture.isOpened():
            print("Erreur : Impossible d'ouvrir la caméra.")
            return
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):

        if self.capture:
            ret, frame = self.capture.read()
            if ret:
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.texture = texture

    def stop_camera(self):
        #Arrete la transmission video et remet l'image par defaut
        if self.capture:
            self.capture.release()
            self.capture = None
        Clock.unschedule(self.update)
        self.source = "ImageInterfaceCamera/ImageArriereFondCamera.png"

class InterfaceDAcceuil(Screen):
    pass
class InterfacePilotage(Screen):
    drone_en_vol = False
    def decoller_atterir_drone(self):#Pas oublier d'ajouter l'effet du drone ici en gros lorsque le drone decolle on donne une vitesse a voir avec Kemuel.
        if self.drone_en_vol:
            self.ids.img_decoller_atterir_drone.source = "ImageInterfaceCamera/ImageDecollerDrone.png"
        else:
            self.ids.img_decoller_atterir_drone.source = "ImageInterfaceCamera/ImageAtterireDrone.png"

        self.drone_en_vol = not self.drone_en_vol


    camera_active = False #Etat de la camera
    def connecter_la_camera(self):

        camera = self.ids.camera_widget
        if not self.camera_active:
            # Active la caméra
            camera.start_camera(0)
            self.ids.btn_toggle.text = "Désactiver la caméra"
        else:
            # Désactive la caméra
            camera.stop_camera()
            self.ids.btn_toggle.text = "Activer la caméra"
            camera.texture = Image(source="ImageInterfaceCamera/ImageArriereFondCamera.png").texture
        self.camera_active = not self.camera_active

    def demarrerHandTracking(self):
        # Ce code nous permet de lancer un autre fichier python dans le fichier python courrant.
        import os
        def run_program():
            os.system('python Simple-Hand-Tracker.py')
        if self.camera_active:
            # CODE A CHANGER TRES IMPORTANT RAISON : Dans le future parce que la camera n'est pas similaire pour les deux.
            print("Desactiver la camera")
        else:
            run_program()




class CameraProjetApp(App):
    def build(self):
        sm = ScreenManager()
        #A decider quelle transition choisir est la meilleur.
        #Permet de choisir le type de transition.
        sm.transition = SwapTransition()
        return sm


if __name__ == '__main__':
    CameraProjetApp().run()