from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

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