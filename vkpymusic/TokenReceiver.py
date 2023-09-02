import os, json, requests, logging
from typing import Callable
from .Client import clients
from .Logger import get_logger

logger: logging = get_logger(__name__)


def on_captcha_handler(url: str) -> str:
    """
    Default handler to captcha.

    Args:
        url (str): Url to captcha image.

    Returns:
        str: Key/decoded captcha.
    """
    logger.info("Are you a bot? You need to enter captcha...")
    os.startfile(url)
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
    def __init__(self, login, password, client="Kate"):
        self.__login: str = str(login)
        self.__password: str = str(password)

        if client in clients:
            self.client = clients[client]
        else:
            self.client = client["Kate"]
        self.__token = None

    def __request_auth(self, code=None, captcha=None):
        session = requests.session()
        session.headers.update({"User-Agent": self.client.user_agent})
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

        request = session.post("https://oauth.vk.com/token", data=query_params)
        session.close()
        return request

    def __request_code(self, sid):
        session = requests.session()
        session.headers.update({"User-Agent": self.client.user_agent})
        query_params = [("sid", str(sid)), ("v", "5.131")]
        response: requests.Response = session.post(
            "https://api.vk.com/method/auth.validatePhone",
            data=query_params,
            allow_redirects=True,
        )
        session.close()

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
        Performs authorization using the available login and password. If necessary, interactively accepts a code from SMS or captcha.

        Args:
            on_captcha (Callable[[str], str]): Handler to captcha. Get url image. Return key.
            on_2fa (Callable[[], str]): Handler to 2 factor auth. Return captcha.
            on_invalid_client (Callable[[], None]): Handler to invalid client.
            on_critical_error (Callable[[Any], None]): Handler to critical error. Get response.

        Returns:
            bool: Boolean value indicating whether authorization was successful or not.
        """
        response_auth: requests.Response = self.__request_auth()
        response_auth_json = json.loads(response_auth.content.decode("utf-8"))

        del self.__login
        del self.__password

        while "error" in response_auth_json:
            error = response_auth_json["error"]

            if error == "need_captcha":
                captcha_sid: str = response_auth_json["captcha_sid"]
                captcha_img: str = response_auth_json["captcha_img"]

                captcha_key: str = on_captcha(captcha_img)

                response_auth = self.__request_auth(captcha=(captcha_sid, captcha_key))
                response_auth_json = json.loads(response_auth.content.decode("utf-8"))

            elif error == "need_validation":
                sid = response_auth_json["validation_sid"]

                # response2: requests.Response =
                self.__request_code(sid)

                # response2_json = json.loads(response2.content.decode('utf-8'))
                code: str = on_2fa()

                response_auth = self.__request_auth(code=code)
                response_auth_json = json.loads(response_auth.content.decode("utf-8"))

            elif error == "invalid_client":
                on_invalid_client()
                return False
            else:
                on_critical_error(response_auth_json)
                self.__on_error(response_auth_json)
                return False
        if "access_token" in response_auth_json:
            access_token = response_auth_json["access_token"]
            logger.info("Token was received!")
            self.__token = access_token
            return True
        self.__on_error(response_auth_json)
        on_critical_error(response_auth_json)
        return False

    def get_token(self) -> str:
        """
        Prints token in console (if authorisation was succesful).
        """
        token = self.__token
        if not token:
            logger.warn('Please, first call the method "auth".')
            return
        logger.info(token)
        return token

    def save_to_config(self, filename: str = "config_vk.ini"):
        """
        Save token and user agent data in config (if authorisation was succesful).

        Args:
            filename (str): Filename of config (default value = "config_vk.ini").
        """
        token: str = self.__token
        if not token:
            logger.warn('Please, first call the method "auth"')
            return
        if os.path.isfile(filename):
            print('File already exist! Enter "OK" for rewriting it')
            if input().lower() != "ok":
                return
        with open(self.create_path("config_vk.ini"), "w") as output_file:
            output_file.write("[VK]\n")
            output_file.write(f"user_agent={self.client.user_agent}\n")
            output_file.write(f"token_for_audio={token}")
            logger.info("Token was saved!")

    @staticmethod
    def create_path(filename: str) -> str:
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, filename)
        return path

    @staticmethod
    def __on_error(response):
        logger.critical(
            "Unexpected error! Please, create an issue in repository for solving this problem."
        )
        logger.critical(response)
