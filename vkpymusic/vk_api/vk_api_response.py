"""
This module contains the VkApiResponse class.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class VkApiResponse:
    """
    A class that represents a response from VK API.

    Attributes:
        data (Any): The data.
    """
    data: Any