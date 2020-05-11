from kivy.app import App

def init_widget(widget):
    widget.app = App.get_running_app()
    widget.screen = widget.app.root.current_screen