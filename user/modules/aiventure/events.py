from typing import *

from aiventure.common.ai import AI
from aiventure.common.adventure import Adventure

from .utils import *


def on_input(in_text: Union[str, List[int]], ai: AI, adventure: Adventure, end: int = None) -> List[int]:
    """
    Fired when text is input to the AI for the purposes of generation.

    :param in_text: The input text.
    :param ai: The AI being used to generate the text.
    :param adventure: The adventure to be generated with.
    :param end: The index of the adventure element to alter. If this is a regular generation, end will be None.
    :return: A list of token IDs to be turned into a tensor before being passed to the AI.
    """
    if in_text is List[int]:
        in_text = ai.decode(in_text)
    end = len(adventure.story) if end is None else end
    in_text = formalize_quotes(in_text).strip()
    context = (' ' + adventure.memory) if adventure.memory else ''
    prompt = ' '.join(adventure.story[:end] + ([in_text] if in_text else []))
    input_tokens = ai.encode(context)
    prompt_tokens = ai.encode(prompt)
    memory = ai.max_memory - ai.max_length - len(input_tokens)
    input_tokens.extend(prompt_tokens[-memory:])
    return input_tokens


def on_output(out_text: str, ai: AI, adventure: Adventure) -> str:
    """
    Fired when text is outputted by the AI following generation.

    :param out_text: The output text.
    :param ai: The AI being used to generate the text.
    :param adventure: The adventure that the text was generated with.
    :return: The final result of the output.
    """
    result = formalize_quotes(out_text).strip()
    result = remove_sentence_fragment(result).strip()
    result = fix_end_quote(result, pre=adventure.story[-1]).strip()
    result = clean_white_space(result).strip()
    return result


def on_display(ai: AI, adventure: Adventure) -> str:
    """
    Fired when the entire adventure is to be displayed.

    :param ai: The AI used to generate the text.
    :param adventure: The adventure to display.
    :return: The final, formatted adventure string.
    """
    story = adventure.story
    result = ''
    for i in range(0, len(story)):
        h = i - 1
        story_elem = story[i].strip()
        if len(story_elem) == 0:
            continue
        story_elem = f'[ref={i}]{story_elem}[/ref]'
        if h < 0:
            result += story_elem
        else:
            end = get_last_sentence_end(story[h])
            if end == len(story[h]):
                result += '\n\n' + story_elem
            else:
                result += ' ' + story_elem
    return result
