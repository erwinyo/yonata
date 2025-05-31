# Built-in imports
import os
import random
import string
import urllib.parse


# Third-party imports
import numpy as np
from PIL import Image


# Local imports


def _generate_unique_id(length=16) -> str:
    random_string = "".join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )
    return random_string


def _decode_url(encoded_url: str) -> str:
    return urllib.parse.unquote(encoded_url)


def _list_to_string(lst: list) -> str:
    """Convert a list to a comma-separated string."""
    return ", ".join(map(str, lst))


def _is_folder_created(folder_name: str, path: str = ".") -> bool:
    return os.path.isdir(os.path.join(path, folder_name))


def _create_folder(folder_name: str, path: str = ".") -> None:
    os.makedirs(os.path.join(path, folder_name), exist_ok=True)
