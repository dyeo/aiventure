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
    :return: Filtered input string.
    """
    return input.strip()

def filter_output(output: str) -> str:
    """
    Default output filter.
    :return: Filtered output string.
    """
    end = find_last_sentence_end(output)
    return output[:end+1].strip()

def filter_display(story: list) -> str:
    result = ''
    for i in range(0, len(story)):
        h = i - 1
        if h < 0 or story[h][-1] == '"':
            result += story[i]
        else:
            end = find_last_sentence_end(story[h])
            if end == len(story[h][-1]):
                result += '\n' + story[i]
            else:
                result += ' ' + story[i]
    return result