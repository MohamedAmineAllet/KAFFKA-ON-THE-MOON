from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window

Window.clearcolor = (79 / 255, 121 / 255, 66 / 255, 1)


class PremiereInterface(Widget):
    pass
    # def press(self):
    #   self.nombreDeClique +=1
    #  print("Bouton appuyé",self.nombreDeClique,"fois")


class CameraProjetApp(App):
    def build(self):
        return PremiereInterface()


if __name__ == '__main__':
    CameraProjetApp().run()