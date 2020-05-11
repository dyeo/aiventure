import os
import json
import threading

from kivy.logger import Logger
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

from aiventure.utils import init_widget
from aiventure.ai.ai import AI
from aiventure.ai.generator import LocalGenerator
from aiventure.play.adventure import Adventure

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def __init__(self, **kargs):
        super(SelectableLabel, self).__init__(**kargs)
        init_widget(self)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)  
      
    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        pass


class SelectableModelLabel(SelectableLabel):
    def apply_selection(self, rv, index, is_selected):
        is_reselected = self.selected == is_selected
        self.selected = is_selected
        if is_selected and not is_reselected:
            self.screen.on_model_selected(self.parent.parent.data[index]['text'])


class SelectableGameLabel(SelectableLabel):
    def apply_selection(self, rv, index, is_selected):
        is_reselected = self.selected == is_selected
        self.selected = is_selected
        if is_selected and not is_reselected:
            self.screen.on_game_selected(self.parent.parent.data[index]['text'])


class MenuScreen(Screen):
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = App.get_running_app()
        self.savefiles = {}
        self.selected_savefile = None

    def on_enter(self):
        self.app.adventure = Adventure()
        self.init_models()
        self.init_saves()
        self.update_button_start_new()
        self.update_button_start_load()
    
    # AI MODEL TAB

    def init_models(self):        
        self.ids.view_model.data = [{'text': str(m)} for m in self.get_module_directories()]

    def get_module_directories(self) -> list:
        return [m.name for m in os.scandir(self.app.get_user_path('models')) if self.model_is_valid(m.path)]

    def model_is_valid(self, modelpath) -> bool:
        return os.path.isfile(os.path.join(modelpath, 'pytorch_model.bin')) \
            and os.path.isfile(os.path.join(modelpath, 'config.json')) \
            and os.path.isfile(os.path.join(modelpath, 'vocab.json'))

    def load_ai(self):
        threading.Thread(target=self._load_ai_thread).start()
        
    def on_model_selected(self, model):
        self.app.settings['ai']['model'] = model
        self.ids.button_load_model.disabled = False

    def _load_ai_thread(self):
        self.ids.button_load_model.disabled = True
        model_path = self.app.get_model_path()
        model_name = os.path.split(model_path)[-1]
        try:
            self.ids.label_model.text = f'Loading Model "{model_name}"'
            Logger.info(f'AI: Loading model at "{model_path}"')
            self.app.generator = LocalGenerator(AI(model_path))
            Logger.info(f'AI: Model loaded at "{model_path}"')
        except Exception as e:
            self.ids.label_model.text = f'Error Loading Model "{model_name}"'
        else:
            self.ids.label_model.text = f'Loaded Model: {model_name} ({self.app.generator.ai.model_info})'
            self.on_update()

    def on_update(self):
        self.update_button_start_new()
        self.update_button_start_load()

    # NEW GAME TAB

    def on_start_new(self):
        self.app.adventure.name = self.ids.input_name.text
        self.app.adventure.context = self.ids.input_context.text
        self.app.adventure.actions.append(self.ids.input_prompt.text)
        self.app.sm.current = 'play'

    def update_button_start_new(self):
        if self.app.generator:
            self.ids.button_start_new.text = 'Start Adventure'
            self.ids.button_start_new.disabled = not (
                self.ids.input_name.text.strip() and \
                self.ids.input_context.text.strip() and \
                self.ids.input_prompt.text.strip() \
            )
        else:
            self.ids.button_start_new.text = 'Please Load Model to Start'
            self.ids.button_start_new.disabled = True
    
    # LOAD GAME TAB
    
    def init_saves(self):
        paths = [s.path for s in os.scandir(self.app.get_user_path('adventures')) if s.path.endswith('.json')]
        for p in paths:
            with open(p, 'r') as json_file:
                data = json.load(json_file)
                self.savefiles[data['name']] = data        
        self.ids.view_game.data = [{'text': str(s)} for s in self.savefiles.keys()]

    def on_game_selected(self, game):
        self.selected_savefile = game

    def on_start_load(self):
        self.app.adventure.from_dict(self.savefiles[self.selected_savefile])
        self.app.sm.current = 'play'

    def update_button_start_load(self):        
        if self.app.generator:
            if self.selected_savefile:
                self.ids.button_start_load.text = 'Start Adventure'
                self.ids.button_start_load.disabled = False
            else:
                self.ids.button_start_load.text = 'Select a Save File'
                self.ids.button_start_load.disabled = True
        else:
            self.ids.button_start_load.text = 'Please Load Model to Start'
            self.ids.button_start_load.disabled = True

