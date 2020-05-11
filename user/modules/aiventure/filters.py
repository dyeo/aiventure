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
        h = i - 1
        if h < 0:
            result += story[i]
        else:
            end = find_last_sentence_end(story[h])
            if end == len(story[h]):
                result += '\n' + story[i]
            else:
                result += ' ' + story[i]
    return result