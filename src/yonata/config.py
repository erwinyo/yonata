# Built-in imports
import sys
from datetime import datetime

# Third-party imports

# Local imports
from loguru import logger

DESTINATION_FOLDER_NAME = "yonata_output"

# ------------------------------- [LOGGER] -------------------------------
LEVEL = "INFO"

# Remove default configuration and add new one
logger.remove()
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
