"""
This module contains the VkApiException class.
"""

from typing import Any, Dict


class VkApiException(Exception):
    """
    A class that represents an exception that occurs when interacting with the VK API.

    Attributes:
        error_code (int): The error code.
        error_msg (str): The error message.
        details (dict): Additional error details.
    """
    def __init__(self, error_code: int, error_msg: str, details: Dict[str, Any]):
        """
        Initializes a VkApiException object.

        Args:
            error_code (int): The error code.
            error_msg (str): The error message.
            details (dict): Additional error details.
        """
        super().__init__(f"VK API Error {error_code}: {error_msg}")
        self.error_code = error_code
        self.error_msg = error_msg
        self.details = details