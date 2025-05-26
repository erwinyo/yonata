import os
import sys
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), './src')))

from rich import print

from yonata.files import list_files_inside_a_folder
from yonata.constant import IMAGE_EXTENSIONS

def main():
    folder_path = "/home/user/yonata/local/image"
    list_of_files = list_files_inside_a_folder(
        folder_path, extensions=IMAGE_EXTENSIONS
    )
    print(list_of_files)

if __name__ == "__main__":
    main()