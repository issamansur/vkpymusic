"""
This module contains the Client class.
"""


class Client:
    """A class that stores the user agent string, client ID, and client secret.

    Attributes:
        user_agent (str): The user agent string.
        client_id (str): The client ID.
        client_secret (str): The client secret.
    """

    def __init__(self, user_agent: str, client_id: str, client_secret: str) -> None:
        """
        Initializes a Client object.

        Args:
            user_agent (str): The user agent string.
            client_id (str): The client ID.
            client_secret (str): The client secret.
        """
        self.user_agent = user_agent
        self.client_id = client_id
        self.client_secret = client_secret


KateMobile = Client(
    user_agent="KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)",
    client_id="2685278",
    client_secret="lxhD8OD7dMsqtXIm5IUY",
)


clients = {"Kate": KateMobile}
