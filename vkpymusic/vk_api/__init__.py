"""
This module contains different classes, using for requests to VK API.

Classes:
    VkApiRequest: A class that represents a request.
    VkApiRequestBuilder: A class that builds requests.
    VkApiResponse: A class that represents a response.
    VkApiException: A class that represents an error.

Functions:
    make_request: A function that makes a synchronous request to VK API.
    make_request_async: A function that makes an asynchronous request to VK API.

Constants:
    BASE_URL: A constant that stores the base URL for VK API.
    DEFAULT_PARAMS: A constant that stores the default parameters for VK API.
"""

from .vk_api_request import VkApiRequest
from .vk_api_request_builder import VkApiRequestBuilder
from .vk_api_response import VkApiResponse
from .vk_api_exception import VkApiException
from .vk_api_extensions import (
    make_request,
    make_request_async,
)
from .vk_api_params import (
    BASE_URL,
    DEFAULT_PARAMS,
)

__all__ = [
    "VkApiRequest",
    "VkApiRequestBuilder",
    "VkApiResponse",
    "VkApiException",

    "make_request",
    "make_request_async",

    "BASE_URL",
    "DEFAULT_PARAMS",
]
