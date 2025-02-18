"""
This module contains the 'VkApiRequest' class
"""

from typing import Optional


class VkApiRequest:
    """
    A class that represents a request to VK API.

    Attributes:
        method (str): The HTTP method.
        url (str): The URL.
        headers (dict): The headers.
        params (dict): The parameters.
    """
    method: str
    url: str
    headers: dict
    params: dict

    def __init__(
            self,
            method: str,
            url: str,
            headers: Optional[dict] = None,
            params: Optional[dict] = None,
    ) -> None:
        """
        Initializes a VkApiRequest object.

        Args:
            method (str): The HTTP method.
            url (str): The URL.
            headers (dict): The headers. (default None)
            params (dict): The parameters. (default None)
        """
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.params = params or {}

    def fill_token(self, token: str) -> None:
        self.params["access_token"] = token
    
    def fill_user_agent(self, user_agent: str) -> None:
        self.headers["User-Agent"] = user_agent

