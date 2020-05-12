import re
import time
import json
import threading
import traceback

from kivy.logger import Logger
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup

from aiventure.utils import *
from aiventure.play.adventure import Adventure

re_tag_start = r'\[[^/\[\]]+\]'
re_tag_end = r'\[/[^\[\]]+\]'

class MenuPopup(Popup):
    def __init__(self, **kargs):
        super(MenuPopup, self).__init__(**kargs)
        init_widget(self)

    def on_save(self) -> None:
        savefile = get_save_name(self.app.adventure.name)
        with open(self.app.get_user_path('adventures',f'{savefile}.json'), 'w') as json_file:
            json.dump(self.app.adventure.to_dict(), json_file)
        self.screen.update_display()
        self.dismiss()
        
    def on_load(self) -> None:
        savefile = get_save_name(self.app.adventure.name)
        with open(self.app.get_user_path('adventures',f'{savefile}.json'), 'r') as json_file:
            self.app.adventure.from_dict(json.load(json_file))
        self.screen.update_display()
        self.dismiss()

    def on_quit(self) -> None:
        self.dismiss()
        self.app.sm.current = 'menu'

class PlayScreen(Screen):

    def __init__(self, **kargs):
        super(PlayScreen, self).__init__(**kargs)
        self.app = App.get_running_app()
        self.mode = '' # 'a' for alter

    def on_enter(self) -> None:
        if len(self.app.adventure.results) == 0:
            prompt = self.app.adventure.actions.pop(0)
            self.on_send(prompt)
        else:
            self.update_display()

    def on_send(self, text = None) -> None:
        text = text or self.ids.input.text
        text = self.filter_input(text)
        threading.Thread(target=self._on_send_thread, args=(text,)).start()

    def _on_send_thread(self, text):
        self.ids.input.disabled = True
        self.ids.button_send.disabled = True
        self.enable_bottom_buttons([])
        self.ids.input.text = ''
        try:
            if self.mode == '':
                self.do_action(text)
            elif self.mode == 'a':
                self.alter_last(text)
            elif self.mode == 'c':
                self.edit_context(text)
        except Exception:
            Logger.error(f"AI: {traceback.format_exc()}")
        self.update_display()
        self.ids.input.disabled = False
        self.ids.button_send.disabled = False

    def do_action(self, text) -> None:
        result = self.app.adventure.get_result(self.app.generator, text)
        self.app.adventure.results[-1] = self.filter_output(result)

    def on_alter(self) -> None:
        if self.mode == 'a':
            self._end_alter()
        else:
            self._start_alter()    

    def on_revert(self) -> None:
        self.app.adventure.actions = self.app.adventure.actions[:-1]
        self.app.adventure.results = self.app.adventure.results[:-1]
        self.update_display()
    
    def on_retry(self) -> None:
        action = self.app.adventure.actions[-1]
        self.app.adventure.actions = self.app.adventure.actions[:-1]
        self.app.adventure.results = self.app.adventure.results[:-1]
        self.on_send(action)

    def on_context(self) -> None:
        if self.mode == 'c':
            self._end_context()
        else:
            self._start_context()

    def _start_alter(self) -> None:
            self._set_edit_mode('a', 'Edit', self.ids.button_alter, 'Cancel', self.app.adventure.results[-1])

    def _end_alter(self) -> None:        
            self._set_edit_mode('', 'Send', self.ids.button_alter, 'Alter')
    
    def _start_context(self) -> None:
            self._set_edit_mode('c', 'Edit', self.ids.button_context, 'Cancel', self.app.adventure.context)

    def _end_context(self) -> None:        
            self._set_edit_mode('', 'Send', self.ids.button_context, 'Context')

    def _set_edit_mode(self, mode, send_text, button, button_text, input_text='', update=True):
        self.mode = mode
        self.ids.button_send.text = send_text
        button.text = button_text
        self.ids.input.text = input_text
        if update:
            self.update_display()

    def update_display(self, scroll: bool=True) -> None:
        self.ids.title_text.text = self.app.adventure.name
        if self.mode == 'a':
            self.enable_bottom_buttons([self.ids.button_alter])
        elif self.mode == 'c':
            self.enable_bottom_buttons([self.ids.button_context])
        else:
            buttons = [self.ids.button_menu, self.ids.button_context]
            len_results = len(self.app.adventure.results)
            buttons += [self.ids.button_alter] if len_results > 0 else []
            buttons += [self.ids.button_revert] if len_results > 0 else []
            buttons += [self.ids.button_retry] if len_results > 0 else []
            self.enable_bottom_buttons(buttons)
        if scroll:
            self.ids.scroll_input.scroll_y = 0
        threading.Thread(target=self.update_output).start()

    def update_output(self) -> None:
        prev_text = self.ids.output.text
        next_text = self.filter_display(self.app.adventure.full_story)
        if len(next_text) > len(prev_text):
            end_tags = []
            i = 0
            while i in range(len(prev_text), len(next_text)):           
                raw_show = next_text[:i+1]
                raw_hide = next_text[i+1:]                    
                start_match = re.match(re_tag_start, raw_hide)
                end_match = re.match(re_tag_end, raw_hide)                    
                result = raw_show
                for e in reversed(end_tags):
                    result += e                    
                if start_match:
                    i += len(start_match.group(0))
                    end_tag = re.findall(re_tag_end, raw_hide)[-len(end_tags)-1]
                    end_tags.append(end_tag)                        
                if end_match:
                    i += len(end_match.group(0))
                    del end_tags[-1]                        
                self.ids.output.text = result                    
                i += 1
                time.sleep(0.0333)
        self.ids.output.text = next_text
        print('end')

    def enable_bottom_buttons(self, buttons: list) -> None:
        for b in self.ids.group_bottom.children:
            b.disabled = (b not in buttons)

    def alter_last(self, text: str) -> None:
        self.app.adventure.results[-1] = text
        self._end_alter()

    def edit_context(self, text: str) -> None:
        self.app.adventure.context = text
        self._end_context()

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
