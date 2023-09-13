import os, datetime, logging


class bcolors:
    CRITICAL = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    ENDC = "\033[0m"


_log_format = "%(asctime)s | [%(name)s | (%(filename)s) .%(funcName)s(%(lineno)d)] [%(levelname)s] %(message)s"


def get_file_handler():
    file_path = f"logs/vkpymusic_{datetime.date.today()}.log"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger
