from kivy.app import App
from kivy.uix.screenmanager import Screen

class PlayScreen(Screen):

    def on_enter(self):
        self.app = App.get_running_app()
        self.ids.input.hint = 'Enter a starting context. eg. "You are a farmer in a countryside village."'
        self.update_output()

    def on_send(self):
        text = self.ids.input.text
        text = text.strip()
        self.ids.input.text = ''
        if self.app.adventure.context == '':
            self.app.adventure.context = text
            self.ids.input.hint = 'Enter an inciting incident. eg. "You are plowing the fields, when suddenly"'
        else:
            self.app.adventure.get_filtered_result(text)
            self.ids.input.hint = 'Enter an action. eg. "You attack the orc with your scythe."'
        self.update_output()

    def update_output(self):
        self.ids.output.text = self.app.adventure.displayed_story
