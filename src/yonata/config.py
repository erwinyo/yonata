# Built-in imports
import sys
from datetime import datetime

# Third-party imports
import psycopg2
from minio import Minio

# Local imports
from loguru import logger

# ------------------------------- [LOGGER] -------------------------------
# LEVEL = "TRACE"
# LEVEL = "DEBUG"
LEVEL = "SUCCESS"

logger.remove()  # Remove default logger configuration
# Add new logger configuration to write to a file
logger.add(
    f"logs/{LEVEL}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
    format="<yellow>[{time:YYYY-MM-DD HH:mm:ss:SSSS}]</yellow> [<level><b>{level}</b></level>] [<b>{file.path}:{line}</b>] [<b>{function}</b>] <level>{message}</level>",
    level=LEVEL,
)
# Add new logger configuration to print to console
logger.add(
    sys.stdout,
    format="<yellow>[{time:YYYY-MM-DD HH:mm:ss:SSSS}]</yellow> [<level><b>{level}</b></level>] [<b>{file.path}:{line}</b>] [<b>{function}</b>] <level>{message}</level>",
    level=LEVEL,
)

# ------------------------------- [DATABASE] -------------------------------
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DBNAME = "postgres"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
_postgres_connection = psycopg2.connect(
    dbname=POSTGRES_DBNAME,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
)
_postgres_cursor = _postgres_connection.cursor()

# ------------------------------- [MINIO] -------------------------------
MINIO_HOST = "localhost"
MINIO_PORT = "9000"
MINIO_USER = "minioadmin"
MINIO_PASSWORD = "minioadmin"
MINIO_BUCKET = "yonata"
MINIO_SECURE = False
_minio_client = Minio(
    f"{MINIO_HOST}:{MINIO_PORT}",
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
)
