import os

from kivy.logger import Logger
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

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
        self.selected = is_selected
        if is_selected:
            App.get_running_app().settings['ai']['model'] = self.parent.parent.data[index]

class MenuScreen(Screen):
    
    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self):
        self.app = App.get_running_app()
        self.modelsdir = self.app.get_user_path('models')    
        self.ids.view_model.data = [{'text': str(m)} for m in self.get_module_directories()]
    
    def get_module_directories(self) -> list:
        return [m.name for m in os.scandir(self.modelsdir) if self.model_is_valid(m.name)]

    def model_is_valid(self, model) -> bool:
        return os.path.isfile(os.path.join(self.modelsdir, model, 'pytorch_model.bin')) \
            and os.path.isfile(os.path.join(self.modelsdir, model, 'config.json')) \
            and os.path.isfile(os.path.join(self.modelsdir, model, 'vocab.json'))

