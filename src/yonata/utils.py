# Built-in imports
import random
import string
import urllib.parse

# Third-party imports

# Local imports


def _generate_unique_id() -> str:
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    return random_string


def _decode_url(encoded_url: str) -> str:
    return urllib.parse.unquote(encoded_url)
