from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Package
from .files import (
    list_files_inside_a_folder
)
from .benchmark import (
    benchmark_from_image_folder
)