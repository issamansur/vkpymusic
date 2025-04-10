"""
Default handlers for VK API.
These handlers are used to process various events
"""

from typing import Dict

##########
# HANDLERS


# sync
def on_captcha_handler(url: str) -> str:
    """
    Default sync handler to captcha.

    Args:
        url (str): Url to captcha image.

    Returns:
        str: Key/decoded captcha.
    """
    print(f"Captcha image: {url}")
    captcha_key: str = input("Captcha: ")
    return captcha_key


def on_2fa_handler() -> str:
    """
    Default sync handler to 2fa.

    Returns:
        str: code from VK/SMS.
    """
    code = input("Code: ")
    return code


def on_invalid_client_handler():
    """
    Default sync handler to invalid_client.
    """
    pass


def on_critical_error_handler(response_or_error: Dict):
    """
    Default sync handler to critical error.

    Args:
        response_auth_json (...): Message or object to research.
    """
    pass


# async
async def on_captcha_handler_async(url: str) -> str:
    """
    Default async handler to captcha.

    Args:
        url (str): Url to captcha image.

    Returns:
        str: Key/decoded captcha.
    """
    print(f"Captcha image: {url}")
    captcha_key: str = await input("Captcha: ")
    return captcha_key


async def on_2fa_handler_async() -> str:
    """
    Default async handler to 2fa.

    Returns:
        str: code from VK/SMS.
    """
    code = input("Code: ")
    return code


async def on_invalid_client_handler_async():
    """
    Default async handler to invalid_client.
    """
    pass


async def on_critical_error_handler_async(response_or_error: Dict):
    """
    Default async handler to critical error.

    Args:
        response_auth_json (...): Message or object to research.
    """
    pass
