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

    @property
    def story(self) -> list:
        """
        The user actions and AI results in chronological order.
        This DOES NOT include the story context.
        :return: A list of action and result strings, interspersed, starting with the first action.
        """
        result = [s for p in zip(self.actions, self.results) for s in p]
        return [s for s in result if s and len(s.strip()) > 0]

    @property
    def full_story(self) -> list:
        """
        The user actions and AI results in chronological order.
        This DOES include the story context.
        :return: The story context string, followed by a list of action and result strings, interspersed, starting with the first action.
        """
        if self.context:
            return [self.context] + self.story
        else:
            return self.story

    def get_result(self, action: str, record: bool = True) -> str:
        """
        Gets a result from the AI, taking into account the existing chat.
        :param action: The action the user has submitted to the AI.
        :param record: Should the result be recorded to the story?
        :return: An acceptable result from the AI.
        """
        temp_story = self.full_story
        if action:
            temp_story += [action]
        temp_story = '\n'.join(self.full_story)
        result = self.ai.generate(temp_story)
        if record:
            self.actions.append(action)
            self.results.append(result)
        return result

