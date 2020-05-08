import os
import sys
import importlib

from kivy.logger import Logger
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang.builder import Builder

from aiventure.utils.settings import Settings
from aiventure.uix.menu import MenuScreen
from aiventure.uix.loadmodel import LoadModelScreen
from aiventure.uix.play import PlayScreen

class AIventureApp(App):

	def build(self) -> ScreenManager:
		"""
		"""
		self.title = 'AIventure'
		self.init_settings()
		self.init_ai()
		self.init_mods()
		self.init_ui()
		return self.sm

	def init_settings(self) -> None:
		"""
		"""
		self.settings = Settings('settings.json', {
			'general': {
				'userdir':'user'
			},
			'ai': {
				'model':'gpt2-xl',
				'gen_length':60,
				'batch_size':1,
				'temperature':0.8,
				'top_k':40,
				'top_p':0.9,
				'rep_pen':1.1
			},
			'modules': {
				'input_filters':['aiventure:filters'],
				'output_filters':['aiventure:filters'],
				'display_filter':'aiventure:filters'
			}
		})

	def init_ai(self) -> None:
		"""
		"""
		self.ai = None
		self.adventure = None

	def init_mods(self) -> None:
		"""
		"""
		sys.path.append(self.settings.get('general','userdir'))

		self.loaded_modules = {}

		self.input_filters = []
		self.output_filters = []
		self.display_filter = None
				
		for f in self.settings.get('modules','input_filters'):
			domain,module = f.split(':')
			Logger.info(f'Modules: Loading {f}.filter_input')
			self.input_filters += [self.load_submodule(domain, module, 'filter_input')]

		for f in self.settings.get('modules','output_filters'):
			domain,module = f.split(':')
			Logger.info(f'Modules: Loading {f}.filter_output')
			self.output_filters += [self.load_submodule(domain, module, 'filter_output')]

		domain,module = self.settings.get('modules','display_filter').split(':')
		Logger.info(f'Modules: Loading {f}.filter_display')
		self.display_filter = self.load_submodule(domain, module, 'filter_display')

	def init_ui(self) -> None:
		"""
		"""
		self.sm = ScreenManager()
		self.screens = { 'menu':MenuScreen, 'loadmodel':LoadModelScreen, 'play':PlayScreen }
		for n,s in self.screens.items():
			Builder.load_file(f'aiventure/uix/{n}.kv')
			self.sm.add_widget(s(name=n))
		self.sm.current = 'menu'

	def get_user_path(self, *args) -> str:
		"""
		"""
		return os.path.join(self.settings.get('general','userdir'), *args)

	def get_model_path(self) -> str:
		return self.get_user_path('models', self.settings.get('ai','model'))

	def get_module_path(self, domain: str, module: str) -> str:
		return self.get_user_path('modules', domain, f'{module}.py')

	def load_module(self, domain: str, module: str) -> None:
		k = f'{domain}:{module}'
		v = self.loaded_modules.get(k)
		if k not in self.loaded_modules:
			v = importlib.import_module(f'.{module}', f'modules.{domain}')
			self.loaded_modules[k] = v
		return v

	def load_submodule(self, domain: str, module: str, submodule: str) -> str:
		m = self.load_module(domain, module)
		return getattr(m, submodule)


if __name__ == "__main__":
    AIventureApp().run()
