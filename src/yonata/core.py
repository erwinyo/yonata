# Built-in imports
import os
from typing import List
from dataclasses import dataclass, field

# Third-party imports
import psycopg2
from minio import Minio
from pydantic import BaseModel

# Local imports
from yonata.config import logger
from yonata.constant import IMAGE_EXTENSIONS
from yonata.gui import _run_gui
from yonata.benchmark import _benchmark_from_image_folder
from yonata.database import set_client_database
from yonata.object_storage import set_client_object_storage


class PostgresConnection(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: str


class MinioConnection(BaseModel):
    host: str
    port: str
    access_key: str
    secret_key: str
    secure: bool


@dataclass(frozen=False, kw_only=False, match_args=False, slots=False)
class Yonata:
    postgres_connection: PostgresConnection = field(default_factory=BaseModel)
    minio_connection: MinioConnection = field(default_factory=BaseModel)

    _postgres_connection: psycopg2 = field(init=False, repr=False)
    _postgres_cursor: psycopg2 = field(init=False, repr=False)
    _minio_client: Minio = field(init=False, repr=False)
    _minio_bucket: Minio = field(init=False, repr=False)

    def __post_init__(self) -> None:
        try:
            self._postgres_connection = psycopg2.connect(
                dbname=self.postgres_connection.dbname,
                user=self.postgres_connection.user,
                password=self.postgres_connection.password,
                host=self.postgres_connection.host,
                port=self.postgres_connection.port,
            )
            self._postgres_cursor = self._postgres_connection.cursor()
            logger.success("PostgreSQL connection successful")
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise

        try:
            self._minio_client = Minio(
                f"{self.minio_connection.host}:{self.minio_connection.port}",
                access_key=self.minio_connection.access_key,
                secret_key=self.minio_connection.secret_key,
                secure=self.minio_connection.secure,
            )

            logger.success("MinIO connection successful")
        except Exception as e:
            logger.error(f"MinIO connection failed: {e}")

        # Set the clients globally
        set_client_database(
            postgres_connection=self._postgres_connection,
            postgres_cursor=self._postgres_cursor,
        )
        set_client_object_storage(minio_client=self._minio_client)

        # Run the GUI application
        _run_gui()

    def do_benchmark_from_image_folder(
        self,
        instance: object,
        folder_path: str,
        extensions: list[str] = IMAGE_EXTENSIONS,
    ) -> None:
        """Benchmark the given instance on all images inside a folder.

        Args:
            instance (object): instance of the class of application to benchmark.
            folder_path (str): path to the folder containing images to benchmark.
            extensions (list[str], optional): list of image file extensions to benchmark.
                Defaults to all allowed extensions. Refer to yonata.constant.IMAGE_EXTENSIONS.

        Notes:
            If the folder has subfolders,
            and those subfolders have files that match the extension,
            then those files are also extracted.

        """
        _benchmark_from_image_folder(
            instance=instance, folder_path=folder_path, extensions=extensions
        )
