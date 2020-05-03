import threading
import time

from kivy.app import App
from kivy.uix.screenmanager import Screen

from aiventure.ai import AI
from aiventure.play.adventure import Adventure

class SplashScreen(Screen):

    def on_enter(self):
        self.app = App.get_running_app()
        threading.Thread(target=self.load_ai, args=('user/models/vanilla-l',)).start()
        pass

    def load_ai(self, model_path):
        self.app.ai = AI(model_path)
        self.app.adventure = Adventure(self.app.ai, '')
        self.app.sm.current = 'play'
        pass