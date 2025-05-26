# Built-in package
import time
import json

# Third-party package
import cv2
from openai import OpenAI
from deepdiff import DeepDiff

# Local package
from .files import list_files_inside_a_folder
from .constant import IMAGE_EXTENSIONS
from .database import (
    insert_to_postgres
)
from .utils import (
    generate_unique_id
)

def initiate_write_to_database(
    type: str
) -> str:
    task_id = generate_unique_id()
    insert_to_postgres(
        table_name="task",
        data={
            "task_id": task_id,
            "type": type,
            "status": "open"
        }
    )
    return task_id

def store_benchmark_result_to_database(
    result: list,
    task_id: str,
) -> None:
    # Input additional mandatory fields
    process_id = generate_unique_id()
    result["process_id"] = process_id
    result["task_id"] = task_id

    insert_to_postgres(
        table_name="process",
        data=result
    )

def benchmark_from_image_folder(
    instance: object,
    folder_path: str,
) -> list:
    task_id = initiate_write_to_database(type="image_folder")
    list_of_files = list_files_inside_a_folder(folder_path, extensions=IMAGE_EXTENSIONS)
    
    # Print the number of files found and their paths
    print(f"Found {len(list_of_files)} files in folder: {folder_path}")
    for idx, file_path in enumerate(list_of_files):
        print(f"[green][{idx}][/green] {file_path}")
    
    for file_path in list_of_files: 
        image = cv2.imread(file_path)
        try:
            start = time.time()
            result = instance.process(image)
            end = time.time()
            time_taken = end - start 
            result = {
                "file_path": file_path,
                "result": result,
                "status": "success",
                "time_taken": time_taken,
            }
        except Exception as e:
            print(f"[red]Error processing file:[/red] {file_path}: {e}")
            result = {
                "file_path": file_path,
                "result": None,
                "status": "failed",
                "time_taken": None,
            }
    
        store_benchmark_result_to_database(
            results=result,
            task_id=task_id
        )




    








# def multimodal_openai(
#     base64_image: str,
#     model: OpenAI,
#     model_name: str,
#     temperature: float,
#     system_prompt: str,
#     prompt: tuple,
#     schema: dict,
#     top_p: float,
#     expected_output: dict
# ) -> dict:
#     response = do_multimodal_with_openai(
#         base64_image=base64_image,
#         system_prompt=system_prompt,
#         prompt=prompt,
#         schema=schema,
#         model=model,
#         model_name=model_name,
#         temperature=temperature,
#         top_p=top_p
#     )
#     response = json.loads(response.output_text)
    
    
#     element_count = count_elements(response)
#     diff = DeepDiff(
#         expected_output,
#         response,
#         ignore_order=True,
#         significant_digits=2
#     )

#     # Count the number of differences (e.g. {'type_changes': 1, 'values_changed': 3})
#     res = {}
#     for d in diff.keys():
#         res[d] = len(diff[d].keys())
#     diff_count = sum(res.values())

#     diff_percentage = (diff_count / element_count) * 100

#     return MultimodalOpenAIOutput(
#         metadata={
#             "model_name": model_name,
#             "temperature": temperature,
#             "top_p": top_p,
#             "prompt": prompt
#         },
#         response=response,
#         element_count=element_count,
#         diff=diff,
#         diff_count=diff_count,
#         diff_percentage=diff_percentage
#     )