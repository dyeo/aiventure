def filter_input(input: str) -> str:
    return '> ' + input

def filter_output(output: str) -> str:
    end = max([output.rfind(c) for c in '.!?"'])
    return ': ' + output[:end+1]

def filter_display(story: list) -> str:
    return '\n'.join(story)