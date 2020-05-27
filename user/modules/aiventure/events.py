from aiventure.common.ai import AI
from aiventure.common.adventure import Adventure


def on_input(input: str, ai: AI, adventure: Adventure) -> str:
    pass


def on_output(output: str, ai: AI, adventure: Adventure) -> str:
    pass


def on_display(ai: AI, adventure: Adventure) -> str:
    pass


def on_altergen(input: str, index: int, ai: AI, adventure: Adventure) -> str:
    pass


def on_retry(input: str, ai: AI, adventure: Adventure) -> str:
    pass


def on_revert(ai: AI, adventure: Adventure) -> str:
    pass