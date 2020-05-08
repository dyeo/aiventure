import threading

from kivy.logger import Logger
from kivy.app import App
from kivy.uix.screenmanager import Screen

from aiventure.ai import AI
from aiventure.play.adventure import Adventure

class LoadModelScreen(Screen):

    def on_enter(self):
        self.app = App.get_running_app()
        threading.Thread(target=self.load_ai, args=(self.app.get_model_path(),)).start()
        pass

    def load_ai(self, model_path):
        Logger.info(f'AI: Loading model located at "{model_path}"')
        self.app.ai = AI(
            model_path, 
            generate_count=self.app.settings.get('ai','gen_count'),
            temperature=self.app.settings.get('ai','temperature'),
            top_k=self.app.settings.get('ai','top_k'),
            top_p=self.app.settings.get('ai','top_p'),
            rep_pen=self.app.settings.get('ai','rep_pen')
        )
        Logger.info(f'AI: Model loaded at "{model_path}"')
        self.app.adventure = Adventure(self.app.ai, '')
        self.app.sm.current = 'play'