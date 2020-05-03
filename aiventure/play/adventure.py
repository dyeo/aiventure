from aiventure.ai import AI


class Adventure(object):
    def __init__(
            self,
            ai: AI,
            context: str
    ):
        self.ai = ai
        self.context = context
        self.actions = []
        self.results = []
        self.memory = 20

    @property
    def story(self) -> list:
        """
        The user actions and AI results in chronological order, not including the story context.
        :return: A list of action and result strings, interspersed, starting with the first action.
        """
        res = [s for p in zip(self.actions, self.results) for s in p]
        return [s for s in res if s and len(s.strip()) > 0]

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

    def get_result(self, action: str, record: bool = True) -> str:
        """
        Gets a result from the AI, taking into account the existing chat.
        :param action: The action the user has submitted to the AI.
        :param record: Should the result be recorded to the story?
        :return: An acceptable result from the AI.
        """
        temp_story = self.remembered_story
        if action:
            temp_story += [action]
        temp_story = ' '.join(temp_story) + ' '
        result = self.ai.generate(temp_story)
        if record:
            self.actions.append(action)
            self.results.append(result)
        return result

