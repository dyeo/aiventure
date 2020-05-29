from __future__ import annotations

from kivy.uix.popup import Popup

from aiventure.client.utils import init_widget


class ErrorPopup(Popup):
    """
    A simple error popup.
    """
    def __init__(self, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        init_widget(self)


def create_and_open(text) -> ErrorPopup:
    popup = ErrorPopup()
    popup.ids.error_text = text
    popup.open()
    return popup
