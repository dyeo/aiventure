import re

from kivy.app import App

def get_save_name(name) -> str:
    name = re.sub(r'\s+', '_', name.strip())
    name = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    return name

def init_widget(widget) -> None:
    widget.app = App.get_running_app()
    widget.screen = widget.app.root.current_screen