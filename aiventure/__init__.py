import os
import sys
import importlib

from kivy.logger import Logger
from kivy.app import App as KivyApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang.builder import Builder

from aiventure.utils.settings import Settings
from aiventure.uix.menu import MenuScreen
from aiventure.uix.play import PlayScreen

class AiventureApp(KivyApp):

	def build(self) -> ScreenManager:
		"""
		"""
		self.title = 'AIventure'
		self.init_ai()
		self.init_mods()
		self.init_ui()
		return self.sm

	def build_config(self, config) -> None:
		"""
		"""
		config.setdefaults('general', {
			'userdir':'user'
		})
		config.setdefaults('ai', {
			'model':'gpt2-xl',
			'memory': 20,
			'gen_length': 60,
			'batch_size': 1,
			'temperature': 0.8,
			'top_k': 40,
			'top_p': 0.9,
			'rep_pen': 1.1
		})
		config.setdefaults('modules', {
			'input_filters':'aiventure:filters',
			'output_filters':'aiventure:filters',
			'display_filter':'aiventure:filters'
		})

	def init_ai(self) -> None:
		"""
		"""
		self.generator = None
		self.adventure = None

	def init_mods(self) -> None:
		"""
		"""
		sys.path.append(self.config.get('general','userdir'))

		self.loaded_modules = {}

		self.input_filters = []
		self.output_filters = []
		self.display_filter = None
		
		for f in self.config.get('modules','input_filters').split(','):
			domain,module = f.split(':')
			Logger.info(f'Modules: Loading {f}.filter_input')
			self.input_filters += [self.load_submodule(domain, module, 'filter_input')]

		for f in self.config.get('modules','output_filters').split(','):
			domain,module = f.split(':')
			Logger.info(f'Modules: Loading {f}.filter_output')
			self.output_filters += [self.load_submodule(domain, module, 'filter_output')]

		domain,module = self.config.get('modules','display_filter').split(':')
		Logger.info(f'Modules: Loading {f}.filter_display')
		self.display_filter = self.load_submodule(domain, module, 'filter_display')

	def init_ui(self) -> None:
		"""
		Initializes the screen manager, loads all screen kivy files and their associated python modules.
		"""
		self.sm = ScreenManager()
		self.screens = { 'menu':MenuScreen, 'play':PlayScreen }
		for n,s in self.screens.items():
			Builder.load_file(f'aiventure/uix/{n}.kv')
			self.sm.add_widget(s(name=n))
		self.sm.current = 'menu'

	def get_user_path(self, *args: str) -> str:
		"""
		Retrieves a path relative to the current user directory.
		:param args: The subdirectories / filenames in the user directory.
		:return: A path in the current user directory.
		"""
		return os.path.join(self.config.get('general','userdir'), *args)

	def get_model_path(self) -> str:
		"""
		Gets the path to the currently selected (but not necessarily loaded) AI model.
		:return: The current selected model path.
		"""
		return self.get_user_path('models', self.config.get('ai','model'))

	def get_module_path(self, domain: str, module: str) -> str:
		return self.get_user_path('modules', domain, f'{module}.py')

	def load_module(self, domain: str, module: str) -> None:
		k = f'{domain}:{module}'
		v = self.loaded_modules.get(k)
		if v is None:
			v = importlib.import_module(f'.{module}', f'modules.{domain}')
			self.loaded_modules[k] = v
		return v

	def load_submodule(self, domain: str, module: str, submodule: str) -> str:
		m = self.load_module(domain, module)
		return getattr(m, submodule)