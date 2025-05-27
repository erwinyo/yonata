# Built-in imports
from datetime import timedelta

# Third-party imports
from minio import Minio

# Local imports
from .config import logger
from .utils import _decode_url


def __parse_minio_path(path: str):
    idx = path.find("/")
    bucket_name = path[:idx]
    object_name = path[idx + 1 :]
    return bucket_name, object_name


def _generate_presigned_url_minio(
    minio_client: Minio, minio_path: str, expiration: int
) -> str:
    try:
        bucket_name, object_name = __parse_minio_path(minio_path)
        url = minio_client.presigned_get_object(
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


def _upload_image_bytes_to_minio(
    minio_client: Minio, minio_path: str, data: bytes
) -> None:
    try:
        bucket_name, object_name = __parse_minio_path(minio_path)
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            length=len(data),
            content_type="image/jpeg",
        )

        logger.success(f"Successfully uploaded {object_name} to {bucket_name}.")
    except Exception as e:
        logger.error(f"Failed to upload {object_name} to {bucket_name}: {e}")
