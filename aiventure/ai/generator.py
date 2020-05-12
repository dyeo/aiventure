from aiventure.ai.ai import AI

class Generator(object):
    """
    Abstract class which separates concerns between application logic and AI generation.
    """
    def __init__(self, ai: AI):
        self.ai = ai

    def generate(self, input: str) -> str:
        pass

try:
    from kivy.app import App
except (ModuleNotFoundError, ImportError) as e:
    pass
else:
    class LocalGenerator(Generator):
        """
        Client-facing generator which handles linking of application logic to the AI.
        """
        def __init__(self, ai: AI):
            super(LocalGenerator, self).__init__(ai)
            self.app = App.get_running_app()
    
        def generate(self, input: str) -> str:
            return self.ai.generate(
                input,            
                length=self.app.config.getint('ai','gen_length'),
                batch_size=self.app.config.getint('ai','batch_size'),
                temperature=self.app.config.getfloat('ai','temperature'),
                top_k=self.app.config.getint('ai','top_k'),
                top_p=self.app.config.getfloat('ai','top_p'),
                rep_pen=self.app.config.getfloat('ai','rep_pen'),
            )
