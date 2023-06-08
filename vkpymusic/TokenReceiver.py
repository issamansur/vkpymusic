import os, json, requests
from .Client import clients


class TokenReceiver:
    def __init__(self, login, password, client="Kate"):
        self.__login = str(login)
        self.__password = str(password)

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

    def auth(self) -> bool:
        """
        Performs authorization using the available login and password. If necessary, interactively accepts a code from SMS or captcha.

        Returns:
            bool: Boolean value indicating whether authorization was successful or not.
        """
        response_auth: requests.Response = self.__request_auth()
        response_auth_json = json.loads(response_auth.content.decode("utf-8"))

        while "error" in response_auth_json:
            error = response_auth_json["error"]

            if error == "need_captcha":
                captcha_sid: str = response_auth_json["captcha_sid"]
                captcha_img: str = response_auth_json["captcha_img"]

                print("Are you bot? You need enter captcha")
                os.startfile(captcha_img)
                captcha_key: str = input("Captcha: ")
                response_auth = self.__request_auth(captcha=(captcha_sid, captcha_key))
                response_auth_json = json.loads(response_auth.content.decode("utf-8"))

            elif error == "need_validation":
                sid = response_auth_json["validation_sid"]

                # response2: requests.Response =
                self.__request_code(sid)

                # response2_json = json.loads(response2.content.decode('utf-8'))
                print(
                    "SMS with a confirmation code has been sent to your phone! The code is valid for a few minutes!"
                )
                code = input("Code: ")
                response_auth = self.__request_auth(code=code)
                response_auth_json = json.loads(response_auth.content.decode("utf-8"))

            elif error == "invalid_client":
                print("Неверный логин или пароль")
                return False
            else:
                self.__login
                self.__password
                error(response_auth_json)
                return False
        if "access_token" in response_auth_json:
            access_token = response_auth_json["access_token"]
            print("Токен получен!")
            self.__token = access_token
            return True
        self.__on_error(response_auth_json)
        return False

    def get_token(self):
        """
        Prints token in console (if authorisation was succesful)
        """
        token = self.__token
        if not token:
            print('Please, first call the method "auth"')
            return
        print(token)

    def save_to_config(self):
        """
        Save token and user agent data in config (if authorisation was succesful).
        """
        token: str = self.__token
        if not token:
            print('Please, first call the method "auth"')
            return
        if os.path.isfile("config_vk.ini"):
            print('File already exist! Enter "OK" for rewriting it')
            if input().lower() != "ok":
                return
        with open(self.create_path("config_vk.ini"), "w") as output_file:
            output_file.write("[VK]\n")
            output_file.write(f"user_agent={self.client.user_agent}\n")
            output_file.write(f"token_for_audio={token}")

    @staticmethod
    def create_path(filename: str) -> str:
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, filename)
        return path

    @staticmethod
    def __on_error(response):
        print("Unexpected error! Logs was saved in file - vtm_error.txt")
        print("Please, create an issue in repository for solving this problem")
        with open(TokenReceiver.create_path("vktoken.error.log"), "a") as output_file:
            output_file.write("Error!\n")
            output_file.write(str(response))
