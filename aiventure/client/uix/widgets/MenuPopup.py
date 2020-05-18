from kivy.uix.popup import Popup

from aiventure.client.utils import init_widget


class MenuPopup(Popup):
    """
    The menu popup, with resume, save/load, and exit to main menu options.
    """
    def __init__(self, **kargs):
        super(MenuPopup, self).__init__(**kargs)
        init_widget(self)

    def on_save(self) -> None:
        """
        Triggered when the user saves the adventure using the save button.
        """
        self.app.save_adventure()
        self.screen.on_update()
        self.dismiss()

    def on_load(self) -> None:
        """
        Triggered when the user loads the adventure using the load button.
        """
        self.app.load_adventure()
        self.screen.on_update()
        self.dismiss()

    def on_quit(self) -> None:
        """
        Triggered when the user quits the adventure using the quit button.
        """
        self.dismiss()
        self.app.sm.current = 'menu'