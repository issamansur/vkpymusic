"""
This module contains the 'TokenReceiver' class, which is responsible 
for performing authorization using the available login and password. 
It interacts with the VK API to obtain an access token.
"""

import os
import json
import logging
from typing import Callable, Tuple, Union, Optional

import requests
from requests import Session, Response

from .client import clients
from .utils import get_logger


logger: logging.Logger = get_logger(__name__)


def on_captcha_handler(url: str) -> str:
    """
    Default handler to captcha.

    Args:
        url (str): Url to captcha image.

    Returns:
        str: Key/decoded captcha.
    """
    logger.info("Are you a bot? You need to enter captcha...")
    os.system(url)
    captcha_key: str = input("Captcha: ")
    return captcha_key


def on_2fa_handler() -> str:
    """
    Default handler to 2fa.

    Returns:
        str: code from VK/SMS.
    """
    logger.info(
        "SMS with a confirmation code has been sent to your phone! The code is valid for a few minutes!"
    )
    code = input("Code: ")
    return code


def on_invalid_client_handler():
    """
    Default handler to invalid_client.
    """
    logger.error("Invalid login or password")


def on_critical_error_handler(response_auth_json):
    """
    Default handler to ctitical error.

    Args:
        response_auth_json (...): Message or object to research.
    """
    print(f"on_critical_error: {response_auth_json}")


class TokenReceiver:
    """
    A class that is responsible for performing authorization using
    the available login and password. It interacts with the VK API
    to obtain an access token. The TokenReceiver class provides
    methods for handling captcha, 2-factor authentication,
    and various error scenarios.

    Attributes:
        client (Client): The client object.
        __login (str): The login.
        __password (str): The password.
        __token (str): The token.

    Example usage:
    ```
    >>> receiver = TokenReceiver(login="my_username", password="my_password")
    >>> if receiver.auth():
    ...    receiver.get_token()
    ...    receiver.save_to_config()
    ```
    """

    def __init__(self, login: str, password: str, client: str = "Kate") -> None:
        """
        Initialize TokenReceiver.

        Args:
            login (str): Login to VK.
            password (str): Password to VK.
            client (str): Client to VK (default value = "Kate").
        """
        self.__login: str = str(login)
        self.__password: str = str(password)
        if client in clients:
            self.client = clients[client]
        else:
            self.client = clients["Kate"]
        self.__token = None

    def request_auth(
        self, code: Optional[str] = None, captcha: Optional[Tuple[int, str]] = None
    ) -> Response:
        """
        Request auth from VK.

        Args:
            code (Optional[str]): Code from VK/SMS (default value = None).
            captcha (Optional[Tuple[int, str]]): Captcha (default value = None).

        Returns:
            Response: Response from VK.
        """
        query_params = [
            ("grant_type", "password"),
            ("client_id", self.client.client_id),
            ("client_secret", self.client.client_secret),
            ("username", self.__login),
            ("password", self.__password),
            ("scope", "audio,offline"),
            ("2fa_supported", 1),
            ("force_sms", 1),
            ("v", 5.131),
        ]
        if captcha:
            query_params.append(("captcha_sid", captcha[0]))
            query_params.append(("captcha_key", captcha[1]))
        if code:
            query_params.append(("code", code))
        with Session() as session:
            session.headers.update({"User-Agent": self.client.user_agent})
            response = session.post("https://oauth.vk.com/token", data=query_params)
        return response

    def request_code(self, sid: Union[str, int]):
        """
        Request code from VK.

        Args:
            sid (Union[str, int]): Sid from VK.

        Returns:
            Response: Response from VK.
        """
        query_params = [("sid", str(sid)), ("v", "5.131")]
        with Session() as session:
            session.headers.update({"User-Agent": self.client.user_agent})
            response = session.post(
                "https://api.vk.com/method/auth.validatePhone",
                data=query_params,
                allow_redirects=True,
            )
        response_json = json.loads(response.content.decode("utf-8"))
        # right_response_json = {
        #     "response": {
        #         "type": "general",
        #         "sid": {str(sid)},
        #         "delay": 60,
        #         "libverify_support": False,
        #         "validation_type": "sms",
        #         "validation_resend": "sms"
        #     }
        # }
        return response_json

    def auth(
        self,
        on_captcha: Callable[[str], str] = on_captcha_handler,
        on_2fa: Callable[[], str] = on_2fa_handler,
        on_invalid_client: Callable[[], None] = on_invalid_client_handler,
        on_critical_error: Callable[..., None] = on_critical_error_handler,
    ) -> bool:
        """
        Performs authorization using the available login and password.
        If necessary, interactively accepts a code from SMS or captcha.

        Args:
            on_captcha (Callable[[str], str]): Handler to captcha. Get url image. Return key.
            on_2fa (Callable[[], str]): Handler to 2 factor auth. Return captcha.
            on_invalid_client (Callable[[], None]): Handler to invalid client.
            on_critical_error (Callable[[Any], None]): Handler to critical error. Get response.

        Returns:
            bool: Boolean value indicating whether authorization was successful or not.
        """
        response_auth: requests.Response = self.request_auth()
        response_auth_json = json.loads(response_auth.content.decode("utf-8"))
        while "error" in response_auth_json:
            error = response_auth_json["error"]
            sid = 0
            if error == "need_captcha":
                captcha_sid: str = response_auth_json["captcha_sid"]
                captcha_img: str = response_auth_json["captcha_img"]
                captcha_key: str = on_captcha(captcha_img)
                response_auth = self.request_auth(captcha=(captcha_sid, captcha_key))
                response_auth_json = json.loads(response_auth.content.decode("utf-8"))
            elif error == "need_validation":
                sid = response_auth_json["validation_sid"]
                # response2: requests.Response =
                self.request_code(sid)
                # response2_json = json.loads(response2.content.decode('utf-8'))
                code: str = on_2fa()
                response_auth = self.request_auth(code=code)
                response_auth_json = json.loads(response_auth.content.decode("utf-8"))
            elif error == "invalid_request":
                logger.warn("Invalid code. Try again!")
                code: str = on_2fa()
                response_auth = self.request_auth(code=code)
                response_auth_json = json.loads(response_auth.content.decode("utf-8"))
            elif error == "invalid_client":
                del self.__login
                del self.__password
                on_invalid_client()
                return False
            else:
                del self.__login
                del self.__password
                on_critical_error(response_auth_json)
                self.__on_error(response_auth_json)
                return False
        if "access_token" in response_auth_json:
            del self.__login
            del self.__password
            access_token = response_auth_json["access_token"]
            logger.info("Token was received!")
            self.__token = access_token
            return True
        del self.__login
        del self.__password
        self.__on_error(response_auth_json)
        on_critical_error(response_auth_json)
        return False

    def get_token(self) -> Optional[str]:
        """
        Prints token in console (if authorisation was succesful).
        """
        token = self.__token
        if not token:
            logger.warn('Please, first call the method "auth".')
            return
        logger.info(token)
        return token

    def save_to_config(self, file_path: str = "config_vk.ini"):
        """
        Save token and user agent data in config (if authorisation was succesful).

        Args:
            file_path (str): Filename of config (default value = "config_vk.ini").
        """
        token: str = self.__token
        if not token:
            logger.warn('Please, first call the method "auth"')
            return
        full_fp = self.create_path(file_path)
        if os.path.isfile(full_fp):
            logger.info('File already exist! Enter "OK" for rewriting it')
            if input().lower() != "ok":
                return
        os.makedirs(os.path.dirname(full_fp), exist_ok=True)
        with open(full_fp, "w") as output_file:
            output_file.write("[VK]\n")
            output_file.write(f"user_agent={self.client.user_agent}\n")
            output_file.write(f"token_for_audio={token}")
            logger.info("Token was saved!")

    @staticmethod
    def create_path(file_path: str) -> str:
        """
        Create path before and after this for different funcs.

        Args:
            file_path (str): Relative path to file.

        Returns:
            str: Absolute path to file.
        """
        return os.path.join(os.path.dirname(__file__), file_path)

    @staticmethod
    def __on_error(response):
        logger.critical(
            "Unexpected error! Please, create an issue in repository for solving this problem."
        )
        logger.critical(response)
