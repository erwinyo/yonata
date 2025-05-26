from yonata.files import list_files_inside_a_folder

FOLDER_PATH = "/home/user/yonata/local/image"    

def test_list_files_inside_a_folder_no_extension():
    results = list_files_inside_a_folder(
        folder_path=FOLDER_PATH,
        extensions=[]
    )
    assert len(results) == 0

def test_list_files_inside_a_folder_single_extension():
    results = list_files_inside_a_folder(
        folder_path=FOLDER_PATH,
        extensions=[".jpg"]
    )

    for result in results:
        assert result.endswith(".jpg")

def test_list_files_inside_a_folder_multiple_extension():
    results = list_files_inside_a_folder(
        folder_path=FOLDER_PATH,
        extensions=[".jpg", ".png", ".pdf", ".ris"]
    )

    for result in results:
        assert result.endswith(".jpg") or result.endswith(".png") or result.endswith(".pdf") or result.endswith(".ris")

def test_list_files_inside_a_folder_check_path_exist():
    try:
        list_files_inside_a_folder(
            folder_path=FOLDER_PATH,
            extensions=[".jpg", ".png", ".pdf", ".ris"]
        )
    except FileNotFoundError as e:
        assert str(e) == f"The folder {FOLDER_PATH} does not exist."


