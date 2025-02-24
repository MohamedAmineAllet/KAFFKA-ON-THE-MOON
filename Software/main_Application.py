from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
import cv2
#Biblioteque utile a la transmission video du Rpy vers l'appareil.


class CameraWidget(Image):
    def __init__(self, **kwargs):
        super(CameraWidget, self).__init__(**kwargs)
        # Ouvre la capture de la webcam
        #self.capture = cv2.VideoCapture('http://10.186.13.54:4747/video')
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("Erreur d'ouverture du flux de la webcam.")
        # Planifie l'update à 30 fps
        Clock.schedule_interval(self.update, 1.0/30.0)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Ici, on effectue éventuellement un flip (adaptable selon tes besoins)
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.texture = texture

class InterfaceDAcceuil(Screen):
    pass
class InterfacePilotage(Screen):
    pass
    def press(self):
        import os


        def run_program():
            os.system('python Simple-Hand-Tracker.py')

        run_program()

class CameraProjetApp(App):
    def build(self):
        return ScreenManager()


if __name__ == '__main__':
    CameraProjetApp().run()