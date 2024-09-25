import logging
from logging import StreamHandler, basicConfig
from logging.handlers import TimedRotatingFileHandler
from os import environ, makedirs

from dotenv import load_dotenv

from logger import get_file_path_logger
from NezuNotify.login import Login

load_dotenv(".env", verbose=True)

EMAIL = environ["EMAIL"]
PASSWORD = environ["PASSWORD"]
LOG_DIRECTORY = "logs"

logger = get_file_path_logger(__name__)

if __name__ == "__main__":
    makedirs(LOG_DIRECTORY, exist_ok=True)

    basicConfig(
        level=logging.INFO,
        datefmt="%Y/%m/%d %H:%M:%S",
        format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)s %(message)s",
        handlers=[
            TimedRotatingFileHandler(
                f"{LOG_DIRECTORY}/app.log",
                when="midnight",
                backupCount=30,
                interval=1,
                encoding="utf-8",
            ),
            StreamHandler(),
        ],
    )

    login = Login(username=EMAIL, password=PASSWORD).login()
    logger.info(login)
