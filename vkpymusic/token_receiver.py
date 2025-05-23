"""
This module contains the 'TokenReceiver' class, which is responsible
for performing authorization using the available login and password.
It interacts with the VK API to obtain an access token.
"""

import os
import logging
from typing import Callable, Awaitable, Tuple, Union, Optional, Dict


from .client import clients
from .vk_api import (
    VkApiRequestBuilder,
    VkApiRequest,
    VkApiResponse,
    VkApiException,
    make_request,
    make_request_async,
)
from .utils import (
    on_captcha_handler,
    on_2fa_handler,
    on_invalid_client_handler,
    on_critical_error_handler,
    on_captcha_handler_async,
    on_2fa_handler_async,
    on_invalid_client_handler_async,
    on_critical_error_handler_async,
)
from .utils import create_logger


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
        _logger (logging.Logger): The logger.

    Example usage:
    ```
    >>> receiver = TokenReceiver(login="my_username", password="my_password")
    >>> if receiver.auth():
    ...    receiver.get_token()
    ...    receiver.save_to_config()
    >>> # or
    >>> if asyncio.run(receiver.auth()):
    ...     receiver.get_token()
    ...     receiver.save_to_config()
    ```
    """

    def __init__(
        self,
        login: str,
        password: str,
        client: str = "Kate",
        logger: logging.Logger = create_logger(__name__),
    ) -> None:
        """
        Initialize TokenReceiver.

        Args:
            login (str): Login to VK.
            password (str): Password to VK.
            client (str): Client to VK (default value = "Kate").
            logger (logging.Logger): Logger (default value = my logger).
        """
        self.__login: str = str(login)
        self.__password: str = str(password)
        if client in clients:
            self.client = clients[client]
        else:
            self.client = clients["Kate"]
        self.__token = None
        self._logger = logger

    #################
    # PRIVATE METHODS

    # synchronous
    def __request_auth(
        self, code: Optional[str] = None, captcha: Optional[Tuple[str, str]] = None
    ) -> VkApiResponse:
        request: VkApiRequest = VkApiRequestBuilder.build_req_auth(
            login=self.__login,
            password=self.__password,
            client=self.client,
            code=code,
            captcha=captcha,
        )
        response: VkApiResponse = make_request(request)

        return response

    def __request_code(self, sid: Union[str, int]) -> VkApiResponse:
        request: VkApiRequest = VkApiRequestBuilder.build_req_2fa_code(
            client=self.client,
            sid=sid,
        )
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
        response: VkApiResponse = make_request(request)
        return response

    # asynchronous
    async def __request_auth_async(
        self, code: Optional[str] = None, captcha: Optional[Tuple[str, str]] = None
    ) -> VkApiResponse:
        request: VkApiRequest = VkApiRequestBuilder.build_req_auth(
            login=self.__login,
            password=self.__password,
            client=self.client,
            code=code,
            captcha=captcha,
        )
        response: VkApiResponse = await make_request_async(request)

        return response

    async def __request_code_async(self, sid: Union[str, int]) -> VkApiResponse:
        request: VkApiRequest = VkApiRequestBuilder.build_req_2fa_code(
            client=self.client,
            sid=sid,
        )
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
        response: VkApiResponse = await make_request_async(request)
        return response

    ################
    # PUBLIC METHODS
    def auth(
        self,
        on_captcha: Callable[[str], str] = on_captcha_handler,
        on_2fa: Callable[[], str] = on_2fa_handler,
        on_invalid_client: Callable[[], None] = on_invalid_client_handler,
        on_critical_error: Callable[..., None] = on_critical_error_handler,
    ) -> bool:
        """
        Performs SYNC authorization using the available login and password.
        If necessary, interactively accepts a code from SMS or captcha.

        Args:
            on_captcha (Callable[[str], str]): Handler to captcha. Get url image. Return key.
            on_2fa (Callable[[], str]): Handler to 2-factor auth. Return captcha.
            on_invalid_client (Callable[[], None]): Handler to invalid client.
            on_critical_error (Callable[[Any], None]): Handler to critical error. Get response.

        Returns:
            bool: Boolean value indicating whether authorization was successful or not.
        """
        code: Optional[str] = None
        captcha: Optional[Tuple[str, str]] = None

        while True:
            try:
                response: VkApiResponse = self.__request_auth(
                    captcha=captcha, code=code
                )
                # If we have no errors, remove login and password
                del self.__login
                del self.__password

                token: str = response.data.get("access_token", None)
                if token is not None:
                    self._logger.info("Token was received!")
                    self.__token = token
                    return True

                # If request was successful, but we have no token
                self.__on_error(response)
                on_critical_error(response)
                return False
            except VkApiException as e:
                problem_response: Dict = e.details

                error = problem_response.get("error", None)
                error_type = problem_response.get("error_type", None)

                # If we have an error, but we don't know how to handle it
                if error is None and error_type is None:
                    self.__on_error(e.details)
                    on_critical_error(e)
                    return False

                # Captcha is needed
                if error == "need_captcha":
                    self._logger.info("Captcha is needed!")
                    captcha_sid: str = problem_response["captcha_sid"]
                    captcha_img: str = problem_response["captcha_img"]
                    captcha_key: str = on_captcha(captcha_img)
                    captcha = (captcha_sid, captcha_key)
                # 2FA is needed
                elif error == "need_validation":
                    self._logger.info("2fa is needed!")
                    validation_type = problem_response["validation_type"]
                    validation_description = problem_response["error_description"]
                    # 2FA app is needed
                    if validation_type == "2fa_app":
                        self._logger.info("Code from 2FA app is needed!")
                    # Other type of 2FA
                    else:
                        self._logger.info(f"{validation_type} {validation_description}")
                        self._logger.info(
                            "Please, create an issue in repository for adding this type."
                        )
                    # Request code from VK
                    sid = problem_response["validation_sid"]
                    _ = self.__request_code(sid)
                    code = on_2fa()
                # Invalid code for 2FA
                elif error == "invalid_request":
                    self._logger.warning("Invalid code. Try again!")
                    code = on_2fa()
                # Login or password is invalid
                elif error == "invalid_client":
                    self._logger.error("Login or password is invalid!")
                    del self.__login
                    del self.__password
                    on_invalid_client()
                    return False
                # Many unsuccessful attempts
                elif (
                    error == "9;Flood control"
                    or error_type == "password_bruteforce_attempt"
                ):
                    self._logger.error("Password bruteforce attempt!")
                    del self.__login
                    del self.__password
                    return False
                # Undefined error
                # (I can't know all errors due to VK API undocumentation)
                else:
                    del self.__login
                    del self.__password
                    on_critical_error(problem_response)
                    self.__on_error(problem_response)
                    return False

    async def auth_async(
        self,
        on_captcha: Callable[[str], Awaitable[str]] = on_captcha_handler_async,
        on_2fa: Callable[[], Awaitable[str]] = on_2fa_handler_async,
        on_invalid_client: Callable[[], Awaitable[None]] = on_invalid_client_handler_async,
        on_critical_error: Callable[..., Awaitable[None]] = on_critical_error_handler_async,
    ) -> bool:
        """
        Performs ASYNC authorization using the available login and password.
        If necessary, interactively accepts a code from SMS or captcha.

        Args:
            on_captcha (Callable[[str], str]): ASYNC handler to captcha. Get url image. Return key.
            on_2fa (Callable[[], str]): ASYNC handler to 2-factor auth. Return captcha.
            on_invalid_client (Callable[[], None]): ASYNC handler to invalid client.
            on_critical_error (Callable[[Any], None]): ASYNC handler to crit error. Get response.

        Returns:
            bool: Boolean value indicating whether authorization was successful or not.
        """
        code: Optional[str] = None
        captcha: Optional[Tuple[str, str]] = None

        while True:
            try:
                response: VkApiResponse = await self.__request_auth_async(
                    captcha=captcha, code=code
                )
                # If we have no errors, remove login and password
                del self.__login
                del self.__password

                token: str = response.data.get("access_token", None)
                if token is not None:
                    self._logger.info("Token was received!")
                    self.__token = token
                    return True

                # If request was successful, but we have no token
                self.__on_error(response)
                await on_critical_error(response)
                return False
            except VkApiException as e:
                problem_response: Dict = e.details

                error = problem_response.get("error", None)
                error_type = problem_response.get("error_type", None)

                # If we have an error, but we don't know how to handle it
                if error is None and error_type is None:
                    self.__on_error(e.details)
                    await on_critical_error(e)
                    return False

                # Captcha is needed
                if error == "need_captcha":
                    self._logger.info("Captcha is needed!")
                    captcha_sid: str = problem_response["captcha_sid"]
                    captcha_img: str = problem_response["captcha_img"]
                    captcha_key: str = await on_captcha(captcha_img)
                    captcha = (captcha_sid, captcha_key)
                # 2FA is needed
                elif error == "need_validation":
                    self._logger.info("2fa is needed!")
                    validation_type = problem_response["validation_type"]
                    validation_description = problem_response["error_description"]
                    # 2FA app is needed
                    if validation_type == "2fa_app":
                        self._logger.info("Code from 2FA app is needed!")
                    # Other type of 2FA
                    else:
                        self._logger.info(f"{validation_type} {validation_description}")
                        self._logger.info(
                            "Please, create an issue in repository for adding this type."
                        )
                    # Request code from VK
                    sid = problem_response["validation_sid"]
                    _ = await self.__request_code_async(sid)
                    code = await on_2fa()
                # Invalid code for 2FA
                elif error == "invalid_request":
                    self._logger.warning("Invalid code. Try again!")
                    code = await on_2fa()
                # Login or password is invalid
                elif error == "invalid_client":
                    self._logger.error("Login or password is invalid!")
                    del self.__login
                    del self.__password
                    await on_invalid_client()
                    return False
                # Many unsuccessful attempts
                elif (
                    error == "9;Flood control"
                    or error_type == "password_bruteforce_attempt"
                ):
                    self._logger.error("Password bruteforce attempt!")
                    del self.__login
                    del self.__password
                    return False
                # Undefined error
                # (I can't know all errors due to VK API undocumentation)
                else:
                    del self.__login
                    del self.__password
                    on_critical_error(problem_response)
                    self.__on_error(problem_response)
                    return False

    def get_token(self) -> Optional[str]:
        """
        Returns the token if exists.
        """
        token = self.__token
        if not token:
            self._logger.warning('Please, first call the method "auth".')
            return
        self._logger.info(token)
        return token

    def save_to_config(self, file_path: str = "config_vk.ini"):
        """
        Save token and user agent data in config (if authorisation was successful).

        Args:
            file_path (str): Filename of config (default value = "config_vk.ini").
        """
        token: str = self.__token
        if not token:
            self._logger.warning('Please, first call the method "auth"')
            return
        full_fp = self.create_path(file_path)
        if os.path.isfile(full_fp):
            self._logger.warning("File already exist! It will be overwritten.")
        os.makedirs(os.path.dirname(full_fp), exist_ok=True)
        with open(full_fp, "w") as output_file:
            output_file.write("[VK]\n")
            output_file.write(f"user_agent={self.client.user_agent}\n")
            output_file.write(f"token_for_audio={token}")
            self._logger.info("Token was saved!")

    def __on_error(self, response):
        self._logger.critical(
            "Unexpected error! Please, create an issue in repository for solving this problem."
        )
        self._logger.critical(response)

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
