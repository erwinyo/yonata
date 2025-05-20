import os
import sys

from .files import list_files_inside_a_folder

def main():
    print("Hello from the main function!")

    PATH = "/home/user/yonata/example_folder"
    files = list_files_inside_a_folder(PATH)
    for file in files:
        print(file)


if __name__ == "__main__":
    main()