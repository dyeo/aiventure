import re
import os
import sys

class StopThreadException(BaseException):
    """
    Dummy exception for stopping threads using the func_timeout StoppableThread.
    """
    pass


def get_save_name(adventure_name: str) -> str:
    """
    :param adventure_name: The full name of the adventure to get a save name for.
    :return: A formatted string that is the save file name of the adventure.
    """
    adventure_name = re.sub(r'\s+', '_', adventure_name.strip())
    adventure_name = re.sub(r'[^a-zA-Z0-9_-]', '', adventure_name)
    return adventure_name


def is_model_valid(model_path: str) -> bool:
    """
    Determines if the pytorch model at the given path is valid.

    :param model_path: The model path to check.
    :return: `True` if the path is valid, `False` otherwise.
    """
    return os.path.isfile(os.path.join(model_path, 'pytorch_model.bin')) \
        and os.path.isfile(os.path.join(model_path, 'config.json')) \
        and os.path.isfile(os.path.join(model_path, 'vocab.json'))


def split_all(path):
    """
    Splits an entire path into its consecutive parts.

    :param path: The path to split.
    :return: A list of all consecutive parts of the path.
    """
    result = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            result.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            result.insert(0, parts[1])
            break
        else:
            path = parts[0]
            result.insert(0, parts[1])
    return result
