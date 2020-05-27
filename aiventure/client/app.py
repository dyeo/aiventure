import importlib
import json
import os
import re
import sys
from threading import Thread
from typing import *
from types import *

from kivy.app import App as KivyApp
from kivy.config import ConfigParser
from kivy.lang.builder import Builder
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager

from aiventure.common.ai import AI
from aiventure.common.adventure import Adventure
from aiventure.common.utils import get_save_name, is_model_valid, split_all

KIVY_SCREEN_DIR = os.path.join('aiventure', 'client', 'uix')
KIVY_WIDGET_DIR = os.path.join('aiventure', 'client', 'uix', 'widgets')


class App(KivyApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # UI
        self.title: str = 'Aiventure'
        self.sm: Optional[ScreenManager] = None
        self.screens: Dict[str, ClassVar] = {}
        # AI
        self.ai: Optional[AI] = None
        self.adventure: Optional[Adventure] = None
        # Threading
        self.threads: Dict[str, Thread] = {}
        # Modules
        self.available_modules: List[str] = []
        self.loaded_modules: Dict[str, str] = {}
        self.events: Dict[str, List[Callable]] = {}
        self.input_filters: List[Callable[[str], str]] = []
        self.output_filters: List[Callable[[str], str]] = []
        self.display_filter: Optional[Callable[[List[str]], str]] = None

    def build(self) -> ScreenManager:
        """
        """
        self.init_mods()
        self.init_ui()
        return self.sm

    def build_config(self, _) -> None:
        """
        """
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.config.setdefaults('general', {
            'userdir': 'user',
            'autosave': True
        })
        self.config.setdefaults('ai', {
            'timeout': 20.0,
            'max_length': 60,
            'beam_searches': 1,
            'temperature': 0.8,
            'top_k': 40,
            'top_p': 0.9,
            'repetition_penalty': 1.1
        })
        self.config.setdefaults('modules', {
            'input_filters': 'aiventure.filters',
            'output_filters': 'aiventure.filters',
            'display_filter': 'aiventure.filters'
        })
        self.config.write()

    def init_mods(self) -> None:
        """
        Initializes the game's module system and loads mods based on the current configuration.
        """
        sys.path.append(self.config.get('general', 'userdir'))

        # get every subdirectory in modules with an __init__.py
        module_paths = [
            os.path.split(d[0])[-1]
            for d in os.walk(self.get_user_path('modules'))
            if '__init__.py' in d[2]
        ][1:]

        # load them all
        [self.load_module(m) for m in module_paths]

    def init_ui(self) -> None:
        """
        Initializes the screen manager, loads all screen kivy files and their associated python modules.
        """
        self.sm = ScreenManager()

        # Load and build all widget kv files
        for file_name in os.listdir(KIVY_WIDGET_DIR):
            if file_name.endswith('.kv'):
                kv_path = os.path.join(KIVY_WIDGET_DIR, file_name)
                Builder.load_file(kv_path)

        # Load and build all screen kv files
        for file_name in os.listdir(KIVY_SCREEN_DIR):
            if file_name.endswith('.kv'):
                kv_path = os.path.join(KIVY_SCREEN_DIR, file_name)
                Builder.load_file(kv_path)
                # If there is an associated python file in the same directory,
                # load it and make it an available screen to the screen manager
                try:
                    name = os.path.splitext(file_name)[0]
                    class_name = name.capitalize() + 'Screen'
                    py = re.sub(r'[\\\/]', '.', os.path.splitext(kv_path)[0])
                    m = importlib.import_module(py)
                    scls = getattr(m, class_name)
                    self.sm.add_widget(scls(name=name))
                except (ImportError, ModuleNotFoundError):
                    pass

        self.sm.current = 'menu'

    def get_user_path(self, *args: str) -> str:
        """
        Retrieves a path relative to the current user directory.

        :param args: The subdirectories / filenames in the user directory.
        :return: A path in the current user directory.
        """
        return os.path.join(self.config.get('general', 'userdir'), *args)

    def get_model_path(self, model: str) -> str:
        """
        Gets the path to the currently selected (but not necessarily loaded) AI model.

        :param model: The model within the models subdirectory.
        :return: The current selected model path.
        """
        return self.get_user_path('models', model)

    def get_valid_models(self) -> List[str]:
        """
        :return: A list of valid model names, inside {userdir}/models
        """
        return [m.name for m in os.scandir(self.get_user_path('models')) if is_model_valid(m.path)]

    def load_module(self, modulepath: str) -> None:
        """
        Loads a module.

        :param modulepath: The module path, separated by dots.
        """
        module = importlib.import_module(f'modules.{modulepath}')
        self.load_events(module)

    def load_events(self, module: ModuleType):
        event_dict = getattr(module, "events")
        events = [
            (
                k,
                self.load_submodule(f'{module.__name__}.{v}', k)
            )
            for k, v in event_dict.items()
        ]
        for (k, v) in events:
            if self.events.get(k) is None:
                self.events[k] = []
            self.events[k] += [v]

    def load_submodule(self, modulepath: str, submodule: str) -> Any:
        a = importlib.import_module(modulepath)
        return getattr(a, submodule)

    # SAVING AND LOADING

    def save_adventure(self) -> None:
        """
        Saves the current adventure.
        """
        savefile = get_save_name(self.adventure.name)
        with open(self.get_user_path('adventures', f'{savefile}.json'), 'w') as json_file:
            json.dump(self.adventure.to_dict(), json_file, indent=4)

    def load_adventure(self) -> None:
        """
        Loads the current adventure.
        """
        savefile = get_save_name(self.adventure.name)
        with open(self.get_user_path('adventures', f'{savefile}.json'), 'r') as json_file:
            self.adventure.from_dict(json.load(json_file))
