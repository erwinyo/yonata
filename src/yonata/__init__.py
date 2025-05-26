from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Package
from .printers import (
    say_greeting
)
from .files import (
    list_files_inside_a_folder
)
from .benchmark import (
    multimodal_openai
)