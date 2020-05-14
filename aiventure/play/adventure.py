from typing import *


class Adventure(object):
    def __init__(
            self,
            name: str = None,
            context: str = None,
    ):
        self.name: str = name
        self.context: str = context
        self.actions: List[str] = []
        self.results: List[str] = []

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'context': self.context,
            'actions': self.actions,
            'results': self.results
        }

    def from_dict(self, d: Dict[str, Any]):
        self.name = d['name']
        self.context = d['context']
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
        :return: The story context string, followed by a list of action and result strings, interspersed, starting
        with the first action.
        """
        return ([self.context] if self.context else []) + self.story

    def get_remembered_story(self, memory: int, end: int = 0) -> list:
        """
        Retrieves last portion remembered by the AI's memory.
        :param memory: The number of latest actions/results to remember.
        :param end: Where the "end" of the story is. `memory` number of elements (plus context) prior to this
        reverse index will be returned.
        :return: The story context string, followed by a list of the last `self.memory` action and result strings,
        interspersed.
        """
        return ([self.context] if self.context else []) + self.story[end-memory:end]
