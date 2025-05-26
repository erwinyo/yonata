import os

def list_files_inside_a_folder(folder_path: str, extensions=None) -> list[str]:
    """
    List all files inside a folder with specific extensions.

    Args:
        folder_path (str): The path to the folder.
        extensions (list[str], optional): List of file extensions to filter by. Defaults to None.

    Returns:
        list[str]: A list of file paths.
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder {folder_path} does not exist.")

    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"{folder_path} is not a directory.")

    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if extensions is None or any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return sorted(files)

