from prompt_toolkit import prompt as input
from prompt_toolkit import print_formatted_text as print


def output_text(
        text: str,
        end: str = "\n"
) -> None:
    print(text, end=end)


def input_text(
        start: str = "",
        default: str = "",
) -> str:
    return input(start, default=default)


def input_int(
        start: str = "",
        default: int = 0,
        require_input: bool = True,
) -> int:
    if require_input:
        while True:
            try:
                return int(input_text(start=start, default=str(default)))
            except ValueError:
                output_text("Invalid input: expected int.")
    else:
        try:
            return int(input_text(start=start, default=str(default)))
        except ValueError:
            return default


def input_float(
        start: str = "",
        default: float = 0.0,
        require_input: bool = True,
) -> float:
    if require_input:
        while True:
            try:
                return float(input_text(start=start, default=str(default)))
            except ValueError:
                output_text("Invalid input: expected float.")
    else:
        try:
            return float(input_text(start=start, default=str(default)))
        except ValueError:
            return default
