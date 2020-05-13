import re

sentence_ends = [r'\.',r'\!',r'\?',r'"[^"]*"']

def find_last_sentence_end(sentence):
    end = -1
    for c in sentence_ends:
        p_end = [m.end() for m in re.finditer(c,sentence)]
        end = max(end, p_end[-1] if len(p_end) > 0 else -1)
    return end

def filter_input(input: str) -> str:
    """
    Default input filter.
    :param input: The input to filter.
    :return: Filtered input string.
    """
    return input.strip()

def filter_output(output: str) -> str:
    """
    Default output filter.
    :param output: The output to filter.
    :return: Filtered output string.
    """
    end = find_last_sentence_end(output)
    return output[:end+1].strip()

def filter_display(story: list) -> str:
    """
    Default display filter.
    :param story: The story to format.
    :return: Filtered display string. 
    Items which don't end on a proper sentence will be followed by a space,
    while items which do end in a proper sentence will be followed by a newline.
    """
    result = ''
    for i in range(0, len(story)):
        is_action = ((i+1) % 2) == 0
        h = i - 1
        story_elem = story[i].strip()
        if len(story_elem) == 0:
            continue
        ref = 'c'
        if i > 0:
            ref = 'a' if is_action else 'r'
            ref += str(i-1)
        story_elem = f'[ref={ref}]{story_elem}[/ref]'
        story_elem = f'[color=#ffff00]{story_elem}[/color]' if is_action else story_elem
        if h < 0:
            result += story_elem
        else:
            end = find_last_sentence_end(story[h])
            if end == len(story[h]):
                result += '\n\n' + story_elem
            else:
                result += ' ' + story_elem
    return result