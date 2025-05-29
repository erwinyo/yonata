# Built-in imports
import os
import sys

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), "./src")))

# Third-party imports
from rich import print

# Local imports
from yonata.files import _list_files_inside_a_folder
from yonata.constant import IMAGE_EXTENSIONS


def main():
    folder_path = "/home/user/yonata/local/image"
    list_of_files = _list_files_inside_a_folder(
        folder_path, extensions=IMAGE_EXTENSIONS
    )
    print(list_of_files)


def init():
    pass


if __name__ == "__main__":
    main()
