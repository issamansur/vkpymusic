"""
Default handlers for VK API.
These handlers are used to process various events
"""

from typing import Dict

from .captcha import handle_captcha_selenium


##########
# HANDLERS


# sync
def on_captcha_handler(redirect_uri: str) -> str:
    """
    Default sync handler for captcha.
    Opens a browser window for the user to solve VK ID Captcha.

    Args:
        redirect_uri (str): redirect_uri for solving VK ID Captcha.

    Returns:
        str: success_token after captcha is solved.
    """
    print(f"Captcha required. Opening browser...")
    token = handle_captcha_selenium(redirect_uri)
    print(f"Captcha solved.")
    return token


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
        response_or_error (...): Message or object to research.
    """
    pass


# async
async def on_captcha_handler_async(data: Dict) -> str:
    """
    Default async handler for captcha.
    Opens a browser window for the user to solve VK ID Captcha.

    Args:
        data (Dict): Error details from VK API containing redirect_uri.

    Returns:
        str: success_token after captcha is solved.
    """
    redirect_uri: str = data.get('redirect_uri')
    print(f"Captcha required. Opening browser...")
    token = handle_captcha_selenium(redirect_uri)
    print(f"Captcha solved.")
    return token


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
        response_or_error (...): Message or object to research.
    """
    pass
