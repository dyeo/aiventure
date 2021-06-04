from typing import *


class Adventure(object):
    def __init__(
            self,
            name: str = None,
            memory: str = None,
    ):
        self.name: str = name
        self.memory: str = memory
        self.story: List[str] = []

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'memory': self.memory,
            'story': self.story,
        }

    def from_dict(self, d: Dict[str, Any]):
        self.name = d['name']
        self.memory = d['memory']
        self.story = d['story']