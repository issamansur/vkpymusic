"""
This module contains the VkApiResponse class.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class VkApiResponse:
    """
    A class that represents a response from VK API.

    Attributes:
        data (Dict): The data.
    """
    data: Dict

    def __init__(self, data: Dict):
        """
        Initialize the VkApiResponse with the given data.

        Args:
            data (Dict): The data.
        """
        self.data = data
