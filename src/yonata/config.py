# Builtin package
import sys
from datetime import datetime

# Third-party package
import psycopg2

# Local package
from loguru import logger

# ------------------------------- [LOGGER] -------------------------------
# LEVEL = "TRACE"
# LEVEL = "DEBUG"
LEVEL = "SUCCESS"

logger.remove() # Remove default logger configuration
# Add new logger configuration to write to a file
logger.add(
    f"logs/{LEVEL}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
    format="<yellow>[{time:YYYY-MM-DD HH:mm:ss:SSSS}]</yellow> [<level><b>{level}</b></level>] [<b>{file.path}:{line}</b>] [<b>{function}</b>] <level>{message}</level>",
    level=LEVEL
)
# Add new logger configuration to print to console
logger.add(
    sys.stdout,
    format="<yellow>[{time:YYYY-MM-DD HH:mm:ss:SSSS}]</yellow> [<level><b>{level}</b></level>] [<b>{file.path}:{line}</b>] [<b>{function}</b>] <level>{message}</level>",
    level=LEVEL
)

# ------------------------------- [DATABASE] -------------------------------
POSTGRES_DBNAME = "postgres"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
postgres_connection = psycopg2.connect(
    dbname=POSTGRES_DBNAME,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT
)

postgres_cursor = postgres_connection.cursor()