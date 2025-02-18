"""
This module contains the 'VkApiRequest' class
"""

from typing import Optional


class VkApiRequest:
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
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.params = params or {}

    def fill_token(self, token: str) -> None:
        self.params["access_token"] = token
    
    def fill_user_agent(self, user_agent: str) -> None:
        self.headers["User-Agent"] = user_agent

