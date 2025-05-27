# Built-in imports
import os
import time
import json
from enum import Enum

# Third-party imports
import cv2
from rich import print
from openai import OpenAI
from deepdiff import DeepDiff

# Local imports
from .files import _list_files_inside_a_folder
from .constant import IMAGE_EXTENSIONS
from .database import _insert_to_postgres, _update_to_postgres
from .object_storage import _upload_image_bytes_to_minio
from .config import logger, minio_client, MINIO_BUCKET
from .utils import _generate_unique_id


class TaskType(str, Enum):
    IMAGE_FOLDER = "image_folder"
    VIDEO_FOLDER = "video_folder"
    AUDIO_FOLDER = "audio_folder"
    TEXT_FOLDER = "text_folder"
    MULTIMODAL_OPENAI = "multimodal_openai"
    MULTIMODAL_HF = "multimodal_hf"
    MULTIMODAL_CUSTOM = "multimodal_custom"


class TaskStatus(str, Enum):
    OPEN = "open"
    ON_PROGRESS = "on_progress"
    CLOSED = "closed"


class ProcessStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


def __store_task_to_database(type: str) -> str:
    task_id = _generate_unique_id()
    _insert_to_postgres(
        table_name="task",
        data={
            "task_id": task_id,
            "type": type,
            "status": TaskStatus.OPEN.value,
        },
    )
    return task_id


def __store_benchmark_result_to_database(
    result: list,
    task_id: str,
) -> str:
    # Input additional mandatory fields
    process_id = _generate_unique_id()
    result["process_id"] = process_id
    result["task_id"] = task_id

    _insert_to_postgres(table_name="process", data=result)
    return process_id


def __update_task(
    task_id: str,
    status: str = None,
    completed_processes: list[str] = None,
    failed_processes: list[str] = None,
) -> None:
    data = {}
    if status is not None:
        data["status"] = status
    if completed_processes is not None:
        data["completed_processes"] = completed_processes
    if failed_processes is not None:
        data["failed_processes"] = failed_processes

    if data:
        _update_to_postgres(
            table_name="task",
            data=data,
            where={"task_id": task_id},
        )


def benchmark_from_image_folder(
    instance: object,
    folder_path: str,
) -> None:
    task_id = __store_task_to_database(type=TaskType.IMAGE_FOLDER.value)

    list_of_files = _list_files_inside_a_folder(
        folder_path, extensions=IMAGE_EXTENSIONS
    )
    print(f"Found {len(list_of_files)} files in folder: {folder_path}")
    for idx, file_path in enumerate(list_of_files):
        print(f"[green][{idx}][/green] {file_path}")

    success_processes = []
    failed_processes = []
    __update_task(task_id=task_id, status=TaskStatus.ON_PROGRESS.value)
    for file_path in list_of_files:
        filename = os.path.basename(file_path)
        image = cv2.imread(file_path)
        image_bytes = cv2.imencode(".jpg", image)[1].tobytes()

        it_success = False
        try:
            # Upload image to MinIO
            file_path_minio = f"{MINIO_BUCKET}/{task_id}/{filename}"
            _upload_image_bytes_to_minio(
                minio_client=minio_client,
                minio_path=file_path_minio,
                data=image_bytes,
            )

            # Inferencing
            start = time.time()
            result = instance.process(image_bytes)
            end = time.time()
            time_taken = end - start
            result = {
                "file_path": file_path_minio,
                "result": result,
                "status": ProcessStatus.SUCCESS.value,
                "time_taken": time_taken,
            }
            it_success = True
        except Exception as e:
            print(f"[red]Error processing file:[/red] {file_path}: {e}")
            result = {
                "file_path": None,
                "result": None,
                "status": ProcessStatus.FAILED.value,
                "time_taken": None,
            }
            it_success = False

        # Store & Update the task processes
        process_id = __store_benchmark_result_to_database(
            result=result, task_id=task_id
        )
        if it_success:
            success_processes.append(process_id)
        else:
            failed_processes.append(process_id)

        __update_task(
            task_id=task_id,
            completed_processes=success_processes,
            failed_processes=failed_processes,
        )

    # Update task status to closed
    __update_task(task_id=task_id, status=TaskStatus.ON_PROGRESS.value)


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
