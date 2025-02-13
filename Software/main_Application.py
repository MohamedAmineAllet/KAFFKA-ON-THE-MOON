from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
#Biblioteque utile a la transmission video du Rpy vers l'appareil.

from kivy.graphics.texture import Texture
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib


class InterfaceDAcceuil(Screen):
    pass




class InterfacePilotage(Screen):
    pass
    # def press(self):
    #   self.nombreDeClique +=1
    #  print("Bouton appuyé",self.nombreDeClique,"fois")

class CameraProjetApp(App):
    def build(self):
        return ScreenManager()


if __name__ == '__main__':
    CameraProjetApp().run()