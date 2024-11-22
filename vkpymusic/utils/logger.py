"""
This module provides a logger utility for vkpymusic.
"""

import os
import logging
import datetime


class BCOLORS:
    """
    A class that defines color codes for log messages.
    """

    CRITICAL = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    ENDC = "\033[0m"


_log_format = "%(asctime)s | %(filename)s(%(lineno)d) | %(module)s.%(funcName)s(...) | [%(levelname)s] %(message)s"


def _get_file_handler() -> logging.FileHandler:
    """
    Returns a file handler for logging to a file.

    The log file is created in the 'logs' directory with the name 'vkpymusic_<current_date>.log'.

    Returns:
        file_handler: A file handler instance for logging to a file.
    """
    file_path = f"logs/vkpymusic_{datetime.date.today()}.log"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def _get_stream_handler() -> logging.StreamHandler:
    """
    Returns a stream handler for logging to the console.

    Returns:
    - stream_handler: A stream handler instance for logging to the console.
    """
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def create_logger(
        name: str,
        console: bool = True,
        file: bool = True
    ) -> logging.Logger:
    """
    Returns a logger instance with configured handlers.

    Args:
        name (str): The name of the logger.
        console (bool): Whether to enable debug messages in the console.
        file (bool): Whether to enable debug messages in the log file.

    Returns:
        logger (logging.Logger): A logger instance with configured handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
    if console:
        logger.addHandler(_get_stream_handler())
    if file:
        logger.addHandler(_get_file_handler())
    return logger
