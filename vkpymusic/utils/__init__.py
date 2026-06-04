"""
This module contains utilities for conversion and logging.

Classes:
    Converter: A class for performing various conversion operations.
    create_logger: A function for getting or creating a logger.
    download_m3u8_as_mp3_pyav: A function for downloading m3u8 stream and converting to mp3.
"""

from .default_handlers import (
    on_captcha_handler,
    on_2fa_handler,
    on_invalid_client_handler,
    on_critical_error_handler,
    on_captcha_handler_async,
    on_2fa_handler_async,
    on_invalid_client_handler_async,
    on_critical_error_handler_async,
)
from .converter import Converter
from .logger import create_logger
from .m3u8converter import download_m3u8_as_mp3_pyav
from .captcha import handle_captcha_selenium

__all__ = [
    "Converter",
    "create_logger",
    "download_m3u8_as_mp3_pyav",
    "on_captcha_handler",
    "on_2fa_handler",
    "on_invalid_client_handler",
    "on_critical_error_handler",
    "on_captcha_handler_async",
    "on_2fa_handler_async",
    "on_invalid_client_handler_async",
    "on_critical_error_handler_async",
]
