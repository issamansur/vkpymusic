from typing import Any, Dict


class VkApiException(Exception):
    def __init__(self, error_code: int, error_msg: str, details: Dict[str, Any]):
        super().__init__(f"VK API Error {error_code}: {error_msg}")
        self.error_code = error_code
        self.error_msg = error_msg
        self.details = details