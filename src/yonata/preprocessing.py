# Built-in imports
import os
import io
import sys
import math
import base64
from io import BytesIO
from pathlib import Path


# Third-party imports
import cv2
import numpy as np
from PIL import Image

# Local imports
from .constant import *


def _image_file_path_to_bytes(image_file_path):
    image_file = Path(image_file_path)
    assert image_file.is_file(), "The provided image path does not exist."

    with open(image_file, "rb") as f:
        image_bytes = f.read()
    return image_bytes


def _image_numpy_to_bytes(image_numpy):
    # Convert numpy array to bytes
    is_success, buffer = cv2.imencode(".jpg", image_numpy)
    if not is_success:
        raise ValueError("Failed to encode the numpy image")
    return buffer.tobytes()


def _image_ndarray_to_bytes_io(ndarray_image: np.ndarray) -> bytes:
    image_bytes = BytesIO()
    Image.fromarray(ndarray_image).save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    return image_bytes


def _image_to_bytes(image_input, maximum_bytes_size=MB_8):
    # Handle both file path and numpy array inputs
    if isinstance(image_input, str):
        image_bytes = _image_file_path_to_bytes(image_input)
    elif "numpy" in str(type(image_input)):
        image_bytes = _image_numpy_to_bytes(image_input)
    else:
        raise TypeError(
            f"Unsupported input type: {type(image_input)}. Expected str path or numpy array."
        )

    # Check if image needs resizing
    if len(image_bytes) > maximum_bytes_size:
        print(
            f"Image size ({len(image_bytes)/1024/1024:.2f}MB) exceeds limit. Resizing..."
        )

        # Convert bytes to PIL Image
        img = Image.open(io.BytesIO(image_bytes))

        # Start with quality reduction
        quality = 90
        output = io.BytesIO()

        # Try reducing quality first
        img.save(output, format="JPEG", quality=quality)

        # If still too large, reduce quality further
        while output.tell() > maximum_bytes_size and quality > 30:
            output = io.BytesIO()
            quality -= 10
            img.save(output, format="JPEG", quality=quality)

        # If quality reduction wasn't enough, reduce dimensions
        if output.tell() > maximum_bytes_size:
            # Calculate new dimensions to maintain aspect ratio
            width, height = img.size
            ratio = min(1.0, math.sqrt(maximum_bytes_size / len(image_bytes)))
            new_width = int(width * ratio)
            new_height = int(height * ratio)

            # Resize and save
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            output = io.BytesIO()
            resized_img.save(output, format="JPEG", quality=quality)

        # Use the resized image
        output.seek(0)
        image_bytes = output.read()

    # Encode the image to base64
    np_array = np.frombuffer(image_bytes, np.uint8)
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    return base64_image
