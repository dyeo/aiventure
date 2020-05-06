import os
import sys
import importlib

from kivy.logger import Logger
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang.builder import Builder

from aiventure.utils.settings import Settings
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
				'model':'vanilla-s'
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
		sys.path.append(self.settings['general']['userdir'])

		self.loaded_modules = {}

		self.input_filters = []
		self.output_filters = []
		self.display_filter = None
				
		for f in self.settings['modules']['input_filters']:
			domain,module = f.split(':')
			Logger.info(f'Modules: Loading {f}.filter_input')
			self.input_filters += [self.load_submodule(domain, module, 'filter_input')]

		for f in self.settings['modules']['output_filters']:
			domain,module = f.split(':')
			Logger.info(f'Modules: Loading {f}.filter_output')
			self.output_filters += [self.load_submodule(domain, module, 'filter_output')]

		domain,module = self.settings['modules']['display_filter'].split(':')
		Logger.info(f'Modules: Loading {f}.filter_display')
		self.display_filter = self.load_submodule(domain, module, 'filter_display')

	def init_ui(self) -> None:
		"""
		"""
		self.sm = ScreenManager()
		self.screens = { 'loadmodel':LoadModelScreen, 'play':PlayScreen }
		for n,s in self.screens.items():
			Builder.load_file(f'aiventure/uix/{n}.kv')
			self.sm.add_widget(s(name=n))
		self.sm.current = 'loadmodel'

	def get_user_path(self, *args) -> str:
		"""
		"""
		return os.path.join(self.settings['general']['userdir'], *args)

	def get_model_path(self) -> str:
		return self.get_user_path('models', self.settings['ai']['model'])

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
