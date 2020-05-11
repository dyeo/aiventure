import os
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
from aiventure.ai import AI
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
        is_reselected = self.selected == is_selected
        self.selected = is_selected
        if is_selected and not is_reselected:
            self.screen.on_model_selected(self.parent.parent.data[index]['text'])

class MenuScreen(Screen):
    
    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self):
        self.app = App.get_running_app()
        self.ids.view_model.data = [{'text': str(m)} for m in self.get_module_directories()]
    
    def get_module_directories(self) -> list:
        modelsdir = self.app.get_user_path('models')
        return [m.name for m in os.scandir(modelsdir) if self.model_is_valid(m.name, modelsdir)]

    def model_is_valid(self, model, modelsdir) -> bool:
        return os.path.isfile(os.path.join(modelsdir, model, 'pytorch_model.bin')) \
            and os.path.isfile(os.path.join(modelsdir, model, 'config.json')) \
            and os.path.isfile(os.path.join(modelsdir, model, 'vocab.json'))

    def load_ai(self):
        threading.Thread(target=self.load_ai_thread).start()

    def load_ai_thread(self):
        self.ids.button_load_model.disabled = True
        self.ids.button_load_model.text = 'Loading Model, Please Wait...'
        model_path = self.app.get_model_path()
        Logger.info(f'AI: Loading model located at "{model_path}"')
        self.app.ai = AI(model_path)
        Logger.info(f'AI: Model loaded at "{model_path}"')
        self.app.adventure = Adventure(self.app.ai, '')
        self.app.sm.current = 'play'
        self.ids.button_load_model.text = 'Model Ready'

    def on_model_selected(self, model):
        self.app.settings['ai']['model'] = model
        self.ids.button_load_model.disabled = False
        self.ids.button_load_model.text = 'Load Model'

