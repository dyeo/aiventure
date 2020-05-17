from typing import *

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput


def init_widget(widget: Widget) -> None:
    """
    Initializes a kivy widget with some standard members.

    :param widget: The widget to initialize.
    :return:
    """
    widget.app = App.get_running_app()
    widget.screen = widget.app.root.current_screen


def limit_input(input: TextInput, length: int, after: Optional[Callable] = None) -> None:
    """
    Limits the length of an input text box to the specified length.
    Should be called in on_text

    :param input:
    :param length:
    """
    input.text = input.text[:length]
    if after:
        after()
