from typing import *

from kivy.app import App

from aiventure.ai.generator import Generator

class Adventure(object):
    def __init__(
            self,
            name: str = None,
            context: str = None,
            memory: int = 20
    ):
        self.name = name
        self.context = context
        self.memory = memory
        self.actions = []
        self.results = []

    def to_dict(self) -> dict:
        result = {}
        result['name'] = self.name
        result['context'] = self.context
        result['memory'] = self.memory
        result['actions'] = self.actions
        result['results'] = self.results
        return result

    def from_dict(self, d):
        self.name = d['name']
        self.context = d['context'] 
        self.memory = d['memory']  
        self.actions = d['actions'] 
        self.results = d['results']

    @property
    def story(self) -> list:
        """
        The user actions and AI results in chronological order, not including the story context.
        :return: A list of action and result strings, interspersed, starting with the first action.
        """
        return [s for p in zip(self.actions, self.results) for s in p]

    @property
    def full_story(self) -> list:
        """
        The user actions and AI results in chronological order, including the story context.
        :return: The story context string, followed by a list of action and result strings, interspersed, starting with the first action.
        """
        return ([self.context] if self.context else []) + self.story

    @property
    def remembered_story(self) -> list:
        """
        The last portion remembered by the AI's memory.
        :return: The story context string, followed by a list of the last `self.memory` action and result strings, interspersed.
        """
        return ([self.context] if self.context else []) + self.story[-self.memory:]
    
    def get_result(self, generator: Generator, action: str, record: bool = True) -> str:
        """
        Gets a raw result from the AI, taking into account the existing story.
        :param action: The action the user has submitted to the AI.
        :param record: Should the result be recorded to the story?
        :return: An acceptable result from the AI.
        """
        temp_story = self.remembered_story
        if action:
            temp_story += [action]
        temp_story = ' '.join(temp_story) + ' '
        result = generator.generate(temp_story)
        if record:
            self.actions.append(action)
            self.results.append(result)
        return result
