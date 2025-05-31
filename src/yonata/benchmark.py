# Built-in imports
import os
import time
import shutil
from enum import Enum

# Third-party imports
import cv2
import json
from rich import print
from pydantic import BaseModel

# Local imports
from yonata.config import logger, DESTINATION_FOLDER_NAME
from yonata.files import _list_files_inside_a_folder
from yonata.constant import IMAGE_EXTENSIONS, MINIO_BUCKET
from yonata.database import _insert_to_postgres, _update_to_postgres
from yonata.object_storage import _upload_image_bytes_to_minio
from yonata.preprocessing import _image_ndarray_to_bytes_io
from yonata.utils import _generate_unique_id, _create_folder


class BenchmarkMetadata(BaseModel):
    task_id: str
    process_id: str
    file_path: str
    result: dict
    status: str
    time_taken: float


class TableName(str, Enum):
    TASK = "task"
    PROCESS = "process"


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


def __generate_task_id() -> str:
    return _generate_unique_id(length=8)


def __generate_process_id() -> str:
    return _generate_unique_id(length=16)


def __generate_unique_filename() -> str:
    return _generate_unique_id(length=16)


def __store_task_to_database(type: str) -> str:
    task_id = __generate_task_id()
    _insert_to_postgres(
        table_name=TableName.TASK.value,
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
    process_id = __generate_process_id()
    result["process_id"] = process_id
    result["task_id"] = task_id

    _insert_to_postgres(table_name=TableName.PROCESS.value, data=result)
    return process_id


def __update_task_to_database(
    task_id: str,
    status: str = None,
    completed_processes: list[str] = None,
    failed_processes: list[str] = None,
) -> None:
    # If not listed on input, set to None
    data = {}
    if status is not None:
        data["status"] = status
    if completed_processes is not None:
        data["completed_processes"] = completed_processes
    if failed_processes is not None:
        data["failed_processes"] = failed_processes

    if data:
        _update_to_postgres(
            table_name=TableName.TASK.value,
            data=data,
            condition={"task_id": task_id},
        )


def _benchmark_from_image_folder(
    instance: object,
    folder_path: str,
    extensions: list[str] = IMAGE_EXTENSIONS,
) -> None:
    final_results = {}

    # Check if the folder exists
    list_of_files = _list_files_inside_a_folder(folder_path, extensions=extensions)

    # Create necessary folders
    task_id = __generate_task_id()
    destination_root_path = os.path.join(
        DESTINATION_FOLDER_NAME, "image_folder", task_id
    )
    destination_image_folder_path = os.path.join(destination_root_path, "images")
    _create_folder(folder_name=destination_image_folder_path)

    # Copy all images to destination folder (for snapshots)
    for file_path in list_of_files:
        filename = os.path.basename(file_path)
        shutil.copy(file_path, os.path.join(destination_image_folder_path, filename))

    final_results["task_id"] = task_id
    final_results["number_of_files"] = len(list_of_files)

    # Begin benchmarking one file at a time
    benchmarking_results = []
    for file_path in list_of_files:
        temp_result = {}
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1]
        temp_result["file_name"] = filename

        image = cv2.imread(file_path)
        image_bytes = _image_ndarray_to_bytes_io(image)

        try:
            # Inferencing
            start = time.time()
            instance_result = instance.process(image)
            end = time.time()
            time_taken = end - start

            temp_result["results"] = instance_result
            temp_result["status"] = ProcessStatus.SUCCESS.value
            temp_result["time_taken"] = time_taken

            logger.success(f"Success processing file: {file_path}")

        except Exception as e:
            logger.error(f"Error processing file: {file_path}: {e}")

            temp_result["results"] = None
            temp_result["status"] = ProcessStatus.FAILED.value
            temp_result["time_taken"] = None

        benchmarking_results.append(temp_result)

    final_results["files"] = benchmarking_results

    # Save the final results to file
    output_path = os.path.join(destination_root_path, "results.json")
    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=4)
    logger.success(f"Benchmark results saved to: {output_path}")


def _benchmark_from_image_folder_to_database(
    instance: object,
    folder_path: str,
    extensions: list[str] = IMAGE_EXTENSIONS,
) -> None:

    # Check if the folder exists
    list_of_files = _list_files_inside_a_folder(folder_path, extensions=extensions)

    # First time regstering the task
    task_id = __store_task_to_database(type=TaskType.IMAGE_FOLDER.value)

    # Start benchmarking one file at a time
    success_processes = []
    failed_processes = []
    __update_task_to_database(task_id=task_id, status=TaskStatus.ON_PROGRESS.value)
    for file_path in list_of_files:
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1]

        image = cv2.imread(file_path)
        image_bytes = _image_ndarray_to_bytes_io(image)

        it_success = False
        try:
            # Upload image to MinIO using image bytes for faster upload
            file_path_minio = (
                f"{MINIO_BUCKET}/{task_id}/{__generate_unique_filename() + file_ext}"
            )
            _upload_image_bytes_to_minio(minio_path=file_path_minio, data=image_bytes)

            # Inferencing
            start = time.time()
            instance_result = instance.process(image)
            end = time.time()
            time_taken = end - start

            # Prepare the output result to store in the database
            result = {
                "file_path": file_path_minio,
                "result": instance_result,
                "status": ProcessStatus.SUCCESS.value,
                "time_taken": time_taken,
            }
            it_success = True
        except Exception as e:
            logger.error(f"[red]Error processing file:[/red] {file_path}: {e}")

            # Prepare the output result to store in the database
            result = {
                "file_path": None,
                "result": None,
                "status": ProcessStatus.FAILED.value,
                "time_taken": None,
            }
            it_success = False

        # Store & Update the task success and failed processes
        process_id = __store_benchmark_result_to_database(
            result=result, task_id=task_id
        )
        if it_success:
            success_processes.append(process_id)
        else:
            failed_processes.append(process_id)
        __update_task_to_database(
            task_id=task_id,
            completed_processes=success_processes,
            failed_processes=failed_processes,
        )
    else:
        # Update task status to closed when all files already processed
        __update_task_to_database(task_id=task_id, status=TaskStatus.CLOSED.value)
