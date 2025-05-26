import random
import string

def generate_unique_id() -> str:
    """
    Generate a unique identifier with a given prefix.

    Returns:
        str: A unique identifier in the format "{prefix}_{random_string}".
    """
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return random_string