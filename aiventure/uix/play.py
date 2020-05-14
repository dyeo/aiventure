import re
import time
import traceback
import threading

from func_timeout import func_timeout, FunctionTimedOut
from func_timeout.StoppableThread import StoppableThread
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from aiventure.utils import init_widget
from aiventure.utils.threading import StopThreadException

re_tag_start = r'\[[^/\[\]]+\]'
re_tag_end = r'\[/[^\[\]]+\]'


class MenuPopup(Popup):
    def __init__(self, **kargs):
        super(MenuPopup, self).__init__(**kargs)
        init_widget(self)

    def on_save(self) -> None:
        self.app.save_adventure()
        self.screen.on_update()
        self.dismiss()

    def on_load(self) -> None:
        self.app.load_adventure()
        self.screen.on_update()
        self.dismiss()

    def on_quit(self) -> None:
        self.dismiss()
        self.app.sm.current = 'menu'


class ErrorPopup(Popup):
    def __init__(self, **kargs):
        super(ErrorPopup, self).__init__(**kargs)
        init_widget(self)


class PlayScreen(Screen):

    def __init__(self, **kargs):
        super(PlayScreen, self).__init__(**kargs)
        self.app = App.get_running_app()
        self.mode: str = ''
        self.edit_index: int = 0
        self.altergen = False
        self.ids.output_text.bind(on_ref_press=self.on_entry_selected)

    def on_enter(self) -> None:
        if len(self.app.adventure.results) == 0:
            prompt = self.app.adventure.actions.pop(0)
            self.on_send(prompt)
        else:
            self.on_update()

    def on_update(self, scroll: bool = True, clear_input: bool = False) -> None:
        self.ids.title_text.text = self.app.adventure.name
        # update bottom buttons
        buttons = [self.ids.button_menu, self.ids.button_cancel]
        if self.mode == '':
            buttons.remove(self.ids.button_cancel)
            if len(self.app.adventure.results) > 0:
                buttons += [self.ids.button_revert]
                buttons += [self.ids.button_retry]
        else:
            buttons += [self.ids.button_altergen]
        self.enable_bottom_buttons(buttons)
        # optionally clear input text
        if clear_input:
            self.ids.input.text = ''
        # optionally scroll to the bottom
        if scroll:
            self.ids.scroll_input.scroll_y = 0
        # update output text
        if self.app.threads.get('output'):
            self.app.threads['output'].stop(StopThreadException)
        self.app.threads['output'] = StoppableThread(target=self._update_output_thread)
        self.app.threads['output'].start()

    def try_autosave(self) -> None:
        if self.app.config.getboolean('general', 'autosave'):
            self.app.save_adventure()

    # SENDING ACTIONS

    def on_send(self, text=None) -> None:
        text = text or self.ids.input.text
        self.app.threads['send'] = threading.Thread(target=self._on_send_thread, args=(text,))
        self.app.threads['send'].start()

    def _on_send_thread(self, text):
        text = self.filter_input(text)
        self.ids.input.disabled = True
        self.ids.button_send.disabled = True
        self.enable_bottom_buttons([])
        try:
            self._select_send(text)
        except Exception:
            Logger.error(f"AI: {traceback.format_exc()}")
        prev_mode = self.mode
        self.mode = ''
        self.on_update(scroll=(prev_mode == ''), clear_input=True)
        self.try_autosave()
        self.ids.input.disabled = False
        self.ids.button_send.disabled = False

    def _select_send(self, text) -> None:
        if self.altergen:
            text += ' ' + self._generate(text, record=False, end=int(self.edit_index/2))
            self.altergen = False
        if self.mode == '':
            self._generate(text)
        elif self.mode == 'c':
            self.app.adventure.context = text
        elif self.mode == 'a':
            self.app.adventure.actions[self.edit_index] = text
        elif self.mode == 'r':
            self.app.adventure.results[self.edit_index] = text

    def _generate(self, text, record=True, start=0, end=0) -> str:
        try:
            result = func_timeout(
                self.app.config.getfloat('ai', 'timeout'),
                self.app.adventure.get_result,
                args=(self.app.generator, text, record, start, end),
            )
            return self.filter_output(result)
        except FunctionTimedOut:
            popup = ErrorPopup()
            popup.ids.error_text.text = 'The AI took too long to respond.\nPlease try something else.'
            popup.open()
        return None

    def on_entry_selected(self, label, value):
        match = re.match(r'([a-z])([0-9]+)?', value)
        self.mode = match.group(1)
        if match.group(2):
            self.edit_index = int(int(match.group(2))/2)
        if self.mode == 'c':
            self.ids.input.text = self.app.adventure.context
        elif self.mode == 'a':
            self.ids.input.text = self.app.adventure.actions[self.edit_index]
        elif self.mode == 'r':
            self.ids.input.text = self.app.adventure.results[self.edit_index]
        self.on_update(scroll=False)

    # BOTTOM MENU

    def enable_bottom_buttons(self, buttons: list) -> None:
        for b in self.ids.group_bottom.children:
            b.disabled = (b not in buttons)

    def on_revert(self) -> None:
        self.app.adventure.actions = self.app.adventure.actions[:-1]
        self.app.adventure.results = self.app.adventure.results[:-1]
        self.on_update()
        self.try_autosave()

    def on_retry(self) -> None:
        action = self.app.adventure.actions[-1]
        self.app.adventure.actions = self.app.adventure.actions[:-1]
        self.app.adventure.results = self.app.adventure.results[:-1]
        self.on_send(action)

    def on_memory(self) -> None:
        pass

    def on_altergen(self) -> None:
        self.altergen = True
        self.on_send()

    def on_cancel(self) -> None:
        self.mode = ''
        self.on_update(scroll=False,clear_input=True)
        pass

    # OUTPUT AND DISPLAY

    def _update_output_thread(self) -> None:
        prev_text = self.ids.output_text.text
        next_text = self.filter_display(self.app.adventure.full_story)
        text_diff = len(next_text) - len(prev_text)
        try:
            if 0 < text_diff <= 800:
                end_tags = []
                i = len(prev_text)
                print(next_text)
                while i in range(len(prev_text), len(next_text)):
                    raw_show = next_text[:i + 1]
                    raw_hide = next_text[i + 1:]
                    start_match = re.match(re_tag_start, raw_hide)
                    end_match = re.match(re_tag_end, raw_hide)
                    result = raw_show
                    for e in reversed(end_tags):
                        result += e
                    if start_match:
                        i += len(start_match.group(0))
                        end_tag = re.findall(re_tag_end, raw_hide)[-len(end_tags) - 1]
                        end_tags.append(end_tag)
                    elif end_match:
                        i += len(end_match.group(0))
                        end_tags.pop(-1)
                    self.ids.output_text.text = result
                    i += 1
                    time.sleep(0.025)
        except StopThreadException:
            pass
        self.ids.output_text.text = self.filter_display(self.app.adventure.full_story)

    # FILTERING

    def filter_input(self, text: str) -> str:
        result = text
        for f in self.app.input_filters:
            result = f(result)
        return result

    def filter_output(self, text: str) -> str:
        result = text
        for f in self.app.output_filters:
            result = f(result)
        return result

    def filter_display(self, story: list) -> str:
        return self.app.display_filter(story)
