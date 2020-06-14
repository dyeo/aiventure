from typing import *
import re
import time
import traceback
import threading

from func_timeout import func_timeout, FunctionTimedOut
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from aiventure.client.uix.widgets import ErrorPopup
from aiventure.common.utils import StopThreadException

re_tag_start = r'\[[^/\[\]]+\]'
re_tag_end = r'\[/[^\[\]]+\]'


class PlayScreen(Screen):
    """
    The in-game screen.
    """
    def __init__(self, **kargs):
        super(PlayScreen, self).__init__(**kargs)
        from aiventure.client.app import App
        self.app: App = App.get_running_app()
        self.mode: str = ''
        self.edit_index: int = 0
        self.altergen: bool = False
        self.is_sending: bool = False

    def on_enter(self) -> None:
        """
        Called upon entering this screen.
        """
        self.ids.output_text.bind(on_ref_press=self.on_entry_selected)
        if len(self.app.adventure.story) == 1:
            prompt = self.app.adventure.story.pop(0)
            self.on_send(prompt)
        else:
            self.on_update()

    def on_update(self, scroll: bool = True, clear_input: bool = False) -> None:
        """
        Updates all core UI elements on this screen.

        :param scroll: If `True`, scroll the output text label to the end.
        :param clear_input: If `True`, clears the input text.
        """
        self.ids.title_text.text = self.app.adventure.name
        # update bottom buttons
        buttons = [self.ids.button_menu, self.ids.button_cancel]
        if self.mode == '':
            buttons += [self.ids.button_memory]
            buttons.remove(self.ids.button_cancel)
            if len(self.app.adventure.story) > 0:
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
        self.ids.output_text.text = self.filter_display(self.app.adventure.full_story)
        # temporarily disabling fancy text outputting because it's broken
        """
        if self.app.threads.get('output'):
            self.app.threads['output'].stop(StopThreadException)
        self.app.threads['output'] = StoppableThread(target=self._update_output_thread)
        self.app.threads['output'].start()
        """

    def try_autosave(self) -> None:
        """
        Autosaves the current adventure, if and only if the autosave game setting is set to `True`.
        """
        if self.app.config.getboolean('general', 'autosave'):
            self.app.save_adventure()

    # SENDING ACTIONS

    def on_send(self, text: Optional[str] = None) -> None:
        """
        Triggered when button_send is pressed.

        :param text: Override to use a different string instead of the input text.
        """
        text = text or self.ids.input.text
        self.app.threads['send'] = threading.Thread(target=self._on_send_thread, args=(text,))
        self.app.threads['send'].start()

    def _on_send_thread(self, text: str) -> None:
        """
        The thread started that handles AI text generation as well as other operations related to button_send.

        :param text: The text in the input text box when send is pressed.
        """
        self.is_sending = True
        text = self.filter_input(text)
        self.ids.input.disabled = True
        self.ids.button_send.disabled = True
        self.enable_bottom_buttons([])
        error = self._try_send(text)
        prev_mode = self.mode
        self.mode = ''
        self.altergen = False
        self.on_update(scroll=(prev_mode == ''), clear_input=error is None)
        if error is None:
            self.try_autosave()
        self.ids.input.disabled = False
        self.ids.button_send.disabled = False
        self.is_sending = False

    def _try_send(self, text: str) -> Optional[BaseException]:
        """
        Determines and performs the send action depending on the current `mode`.

        :param text: The text to send.
        """
        result = None
        try:
            if self.altergen:
                text
                text += ' ' + \
                        self._generate(text, record=False, end=self.edit_index)
            if self.mode == '':
                self._generate(text)
            elif self.mode == 'c':
                self.app.adventure.context = text
            elif self.mode == 'a':
                self.app.adventure.story[self.edit_index] = text
            elif self.mode == 'm':
                self.app.adventure.memory = text
        except FunctionTimedOut as e:
            result = e
            ErrorPopup.create_and_open('The AI took too long to respond.\nPlease try something else.')
        except Exception as e:
            result = e
            ErrorPopup.create_and_open('The AI ran out of memory.\nPlease try something else.')
            Logger.error(f"AI: {traceback.format_exc()}")
        return result

    def _generate(
        self,
        text: str,
        record: bool = True,
        end: int = None,
    ) -> Optional[str]:
        """
        Tells the AI to generate new text.

        :param text: The input text for the AI to build upon.
        :param record: If True, the input text and the result will be added automatically to the adventure.
        :param end: The entry to start generating from.
        :return: The result of the AI generation, or `None` if the AI timed out.
        """
        self._prime_ai()
        input_ids = self.app.fire_event('on_input', in_text=text, ai=self.app.ai, adventure=self.app.adventure, end=end)
        if record and text:
            self.app.adventure.story.append(text)
        result = self._generate_inner(input_ids)
        result = self.app.fire_event('on_output', out_text=result, ai=self.app.ai, adventure=self.app.adventure)
        if record and result:
            self.app.adventure.story.append(result)
        return result

    def _generate_inner(self, input_ids):
        timeout = self.app.config.getfloat('ai', 'timeout')
        return func_timeout(
            604800.0 if timeout <= 0 else timeout,
            self.app.ai.generate,
            args=(input_ids,),
        )

    def _prime_ai(self):
        self.app.ai.prime(
            self.app.config.getint('ai', 'max_length'),
            self.app.config.getint('ai', 'beam_searches'),
            self.app.config.getfloat('ai', 'temperature'),
            self.app.config.getint('ai', 'top_k'),
            self.app.config.getfloat('ai', 'top_p'),
            self.app.config.getfloat('ai', 'repetition_penalty'),
        )

    def on_entry_selected(self, _, ref) -> None:
        """
        Triggered when a story entry is pressed in the output text.

        :param _: Unused.
        :param ref: The reference string for the story entry.
        'c' for context.
        'a' for any other alteration.
        'a' will be proceeded immediately by a number, which specifies their index in the
        adventure's story.
        """
        if self.is_sending:
            return
        match = re.match(r'([a-z])?([0-9]+)?', ref)
        if match.group(1):
            self.mode = match.group(1)
        if match.group(2):
            self.edit_index = int(match.group(2))
        if self.mode == 'c':
            self.ids.input.text = self.app.adventure.context
        elif self.mode == 'a':
            self.ids.input.text = self.app.adventure.story[self.edit_index]
        self.on_update(scroll=False)

    # BOTTOM MENU

    def enable_bottom_buttons(self, buttons: List[Button]) -> None:
        """
        Enables all bottom-bar buttons in the provided list, and disables all other bottom-bar buttons.

        :param buttons: The buttons in the bottom bar to leave enabled.
        """
        for b in self.ids.group_bottom.children:
            b.disabled = (b not in buttons)

    def on_revert(self) -> None:
        """
        Triggered when button_revert is pressed.
        """
        self.app.adventure.story = self.app.adventure.story[:-1]
        self.on_update()
        self.try_autosave()

    def on_retry(self) -> None:
        """
        Triggered when button_retry is pressed.
        """
        self.app.adventure.story.pop(-1)
        self.on_send(self.app.adventure.story.pop(-1))

    def on_memory(self) -> None:
        """
        Triggered when button_memory is pressed.
        """
        self.mode = 'm'
        self.ids.input.text = self.app.adventure.memory
        self.on_update(scroll=False, clear_input=False)

    def on_altergen(self) -> None:
        """
        Triggered when button_altergen is pressed.
        """
        self.altergen = True
        self.on_send()

    def on_cancel(self) -> None:
        """
        Triggered when button_cancel is pressed.
        """
        self.mode = ''
        self.on_update(scroll=False, clear_input=True)
        pass

    # OUTPUT AND DISPLAY

    def _update_output_thread(self) -> None:
        """
        Updates the output text with a cool scrolling text effect.
        """
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
        """
        Filters the input according to the currently loaded input filters.

        :param text: The input text.
        :return: The filtered input text.
        """
        result = text
        for f in self.app.input_filters:
            result = f(result)
        return result

    def filter_output(self, text: str) -> str:
        """
        Filters the output according to the currently loaded output filters.

        :param text: The output text.
        :return: The filtered output text.
        """
        result = text
        for f in self.app.output_filters:
            result = f(result)
        return result

    def filter_display(self, story: List[str]) -> str:
        """
        Filters the story according to the currently loaded display filters.

        :param story: The story.
        :return: The filtered story text.
        """
        return self.app.fire_event('on_display', ai=self.app.ai, adventure=self.app.adventure)
