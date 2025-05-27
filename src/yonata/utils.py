# Built-in imports
import random
import string
import urllib.parse
from io import BytesIO

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


def _image_ndarray_to_bytes_io(ndarray_image: np.ndarray) -> bytes:
    image_bytes = BytesIO()
    Image.fromarray(ndarray_image).save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    return image_bytes
