"""
This module contains functions for prepare
and making requests to the VK API.
"""

from typing import Dict, Optional

from curl_cffi import requests as curl_requests
from curl_cffi.requests import AsyncSession, Response

from ..vk_api import VkApiRequest, VkApiResponse, VkApiException


def make_request(request: VkApiRequest) -> VkApiResponse:
    """
    Makes a synchronous request to the VK API.

    Args:
        request (VkApiRequest): The request to make.

    Returns:
        VkApiResponse: The response from the VK API.

    Raises:
        VkApiException: If the response status code is not 200.
    """
    response = curl_requests.get(
        url=request.url,
        headers=request.headers,
        params=request.params,
        impersonate="chrome110",
    )

    vk_response: VkApiResponse = _validate_and_parse_response(response)

    return vk_response


async def make_request_async(request: VkApiRequest) -> VkApiResponse:
    """
    Makes an asynchronous request to the VK API.

    Args:
        request (VkApiRequest): The request to make.

    Returns:
        VkApiResponse: The response from the VK API.

    Raises:
        VkApiException: If the response status code is not 200.
    """
    async with AsyncSession() as session:
        response = await session.get(
            url=request.url,
            headers=request.headers,
            params=request.params,
            impersonate="chrome110",
        )

    vk_response: VkApiResponse = _validate_and_parse_response(response)

    return vk_response


def _validate_and_parse_response(
    api_response: Response
) -> VkApiResponse:
    """
    Validate and parse response from VK API.

    Args:
        api_response (VkApiResponse): Response from VK API.
    
    Returns:
        VkApiResponse: Parsed response from VK API.
    """
    # Convert response to json
    api_response_data: Dict = api_response.json()

    # Use None and validate by equals to None,
    # because we can have an empty payload or 0 or False
    payload: Dict = api_response_data.get("response", None)
    error: Dict = api_response_data.get("error", None)

    # If we have payload, return it
    if payload is not None:
        return VkApiResponse(payload)
    # If we have an error, raise an exception
    elif error is not None:
        # If it's a string (OMG, VK API, why?), save entire request
        if isinstance(error, str):
            raise VkApiException(
                0,
                error,
                api_response_data,
            )
        # If it's a dict, raise an exception with error code and message
        elif isinstance(error, dict):
            raise VkApiException(
                error.get("error_code", 0),
                error.get("error_msg", "Unknown error"),
                error,
            )
        # If it's something else, raise an exception
        else:
            raise VkApiException(
                0,
                "Unknown error",
                api_response_data,
            )
    
    # else, return the response (thank you, VK API for different payloads)
    return VkApiResponse(api_response_data)
