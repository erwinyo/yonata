# Built-in imports
from datetime import timedelta

# Third-party imports
from minio import Minio

# Local imports
from yonata.config import logger
from yonata.utils import _decode_url

__minio_client = None


def set_client_object_storage(minio_client: Minio):
    global __minio_client
    __minio_client = minio_client


def __parse_minio_path(path: str):
    idx = path.find("/")
    bucket_name = path[:idx]
    object_name = path[idx + 1 :]
    return bucket_name, object_name


def _generate_presigned_url_minio(minio_path: str, expiration: int) -> str:
    try:
        bucket_name, object_name = __parse_minio_path(minio_path)
        url = __minio_client.presigned_get_object(
            bucket_name=bucket_name, object_name=object_name, expires=expiration
        )
        decoded_url = _decode_url(url)
        logger.success(f"Presigned URL generated for {object_name} in {bucket_name}.")
        return decoded_url
    except Exception as e:
        logger.error(
            f"Failed to generate presigned URL for {object_name} in {bucket_name}: {e}"
        )
        return ""


def _upload_image_bytes_to_minio(minio_path: str, data: bytes) -> None:
    try:
        bucket_name, object_name = __parse_minio_path(minio_path)
        __minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            length=len(data.getvalue()),
            content_type="image/jpeg",
        )

        logger.success(f"Successfully uploaded {object_name} to {bucket_name}.")
    except Exception as e:
        logger.error(f"Failed to upload {object_name} to {bucket_name}: {e}")
