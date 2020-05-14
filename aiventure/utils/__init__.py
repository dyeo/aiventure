import re
import os

from kivy.app import App
from kivy.uix.widget import Widget


def get_save_name(adventure_name: str) -> str:
    """
    :param adventure_name: The full name of the adventure to get a save name for.
    :return: A formatted string that is the save file name of the adventure.
    """
    adventure_name = re.sub(r'\s+', '_', adventure_name.strip())
    adventure_name = re.sub(r'[^a-zA-Z0-9_-]', '', adventure_name)
    return adventure_name


def init_widget(widget: Widget) -> None:
    """
    Initializes a kivy widget with some standard members.

    :param widget: The widget to initialize.
    :return:
    """
    widget.app = App.get_running_app()
    widget.screen = widget.app.root.current_screen


def is_model_valid(model_path: str) -> bool:
    """
    Determines if the pytorch model at the given path is valid.

    :param model_path: The model path to check.
    :return: `True` if the path is valid, `False` otherwise.
    """
    return os.path.isfile(os.path.join(model_path, 'pytorch_model.bin')) \
        and os.path.isfile(os.path.join(model_path, 'config.json')) \
        and os.path.isfile(os.path.join(model_path, 'vocab.json'))
