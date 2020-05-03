from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang.builder import Builder

from aiventure.uix.splash import SplashScreen
from aiventure.uix.play import PlayScreen

class AIventureApp(App):

	def build(self):
		self.title = 'AIventure'
		self.init_ui()
		return self.sm

	def init_ai(self):
		self.ai = None
		self.adventure = None

	def init_ui(self):		
		self.sm = ScreenManager()
		self.screens = { 'splash':SplashScreen, 'play':PlayScreen }		
		for n,s in self.screens.items():
			Builder.load_file(f'aiventure/uix/{n}.kv')
			self.sm.add_widget(s(name=n))
		self.sm.current = 'splash'
