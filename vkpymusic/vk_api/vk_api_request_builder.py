"""
This module contains the 'VkApiRequestBuilder' class
for building requests to VK API.
"""

from typing import Dict, Tuple, Optional, Union

from ..client import Client
from .vk_api_request import VkApiRequest
from .vk_api_params import BASE_URL, DEFAULT_PARAMS, DEFAULT_VERSION


class VkApiRequestBuilder:
    """
    A class for building requests to VK API.
    """

    # Auth section

    @staticmethod
    def build_req_auth(
        login: str,
        password: str,
        client: Client,
        code: Optional[str] = None,
        captcha: Optional[Tuple[str, str]] = None,
    ) -> VkApiRequest:
        """
        Builds a request to get access token.

        Args:
            login (str): The login.
            password (str): The password.
            client (Client): The client.
            code (Optional[str]): Code from VK/SMS (default value = None).
            captcha (Optional[Tuple[str, str]]): Captcha (default value = None).
        """
        url: str = "https://oauth.vk.com/token"

        params: Dict = {
            "grant_type": "password",
            "client_id": client.client_id,
            "client_secret": client.client_secret,
            "username": login,
            "password": password,
            "scope": "audio,offline",
            "2fa_supported": 1,
            "force_sms": 1,
            "v": DEFAULT_VERSION,
        }
        if captcha:
            params.setdefault("captcha_sid", captcha[0])
            params.setdefault("captcha_key", captcha[1])

        if code:
            params.setdefault("code", code)

        request: VkApiRequest = VkApiRequest(
            method="post",
            url=url,
            params=params,
        )

        request.fill_user_agent(client.user_agent)

        return request

    @staticmethod
    def build_req_2fa_code(client: Client, sid: Union[str, int]) -> VkApiRequest:
        """
        Builds a request to get access token.

        Args:
            sid (Union[str, int]): Sid from VK.
        """
        url: str = "https://api.vk.com/method/auth.validatePhone"

        params: Dict = {
            "sid": str(sid),
            "v": DEFAULT_VERSION,
        }

        request: VkApiRequest = VkApiRequest(
            method="post",
            url=url,
            params=params,
        )

        request.fill_user_agent(client.user_agent)

        return request

    # Common section

    @staticmethod
    def build_from_base_request(method: str, url: str, params: dict) -> VkApiRequest:
        """
        Builds a request from a base request.

        Args:
            method (str): The HTTP method.
            url (str): The URL.
            params (dict): The parameters.
        """
        request: VkApiRequest = VkApiRequest(
            method=method,
            url=BASE_URL + url,
            # use {} to unpack the dictionary for py <3.9
            # later we can use params | DEFAULT_PARAMS
            params={**DEFAULT_PARAMS, **params},
        )

        return request

    # Profile section

    @classmethod
    def build_req_get_profile_info(cls) -> VkApiRequest:
        """
        Builds a request to get profile information.
        """
        params: Dict = {}

        return cls.build_from_base_request(
            method="get", url="account.getProfileInfo", params=params
        )

    # Audio section

    @classmethod
    def build_req_get_count(cls, userid: int) -> VkApiRequest:
        """
        Builds a request to get the number of user's audio.

        Args:
            userid (int): The user ID.
        """
        params: Dict = {"owner_id": userid}

        return cls.build_from_base_request(
            method="get", url="audio.getCount", params=params
        )

    @classmethod
    def build_req_get(
        cls,
        userid: int,
        count: int = 100,
        offset: int = 0,
        playlist_id: Optional[int] = None,
        access_key: Optional[str] = None,
    ) -> VkApiRequest:
        """
        Builds a request to get user's audio.

        Args:
            userid (int): The user ID.
            count (int): The number of audio recordings. (default 100)
            offset (int): The offset. (default 0)
            playlist_id (int): The playlist ID. (default None)
            access_key (str): The access key. (default None)
        """
        params: Dict = {
            "owner_id": userid,
            "count": count,
            "offset": offset,
        }

        if playlist_id:
            params["album_id"] = playlist_id
            params["access_key"] = access_key

        return cls.build_from_base_request(method="get", url="audio.get", params=params)

    @classmethod
    def build_req_search(
        cls,
        query: str,
        count: int = 100,
        offset: int = 0,
    ) -> VkApiRequest:
        """
        Builds a request to search for audio by query.

        Args:
            query (str): The query.
            count (int): The number of audio recordings. (default 100)
            offset (int): The offset. (default 0)
        """
        params: Dict = {
            "q": query,
            "count": count,
            "offset": offset,
            "sort": 0,
            "autocomplete": 1,
        }

        return cls.build_from_base_request(
            method="get", url="audio.search", params=params
        )

    @classmethod
    def build_req_get_playlists(
        cls,
        userid: int,
        count: int = 50,
        offset: int = 0,
    ) -> VkApiRequest:
        """
        Builds a request to get user's playlists.

        Args:
            userid (int): The user ID.
            count (int): The number of playlists. (default 50)
            offset (int): The offset. (default 0)
        """
        params: Dict = {
            "owner_id": userid,
            "count": count,
            "offset": offset,
        }

        return cls.build_from_base_request(
            method="get", url="audio.getPlaylists", params=params
        )

    @classmethod
    def build_req_search_playlists(
        cls,
        text: str,
        count: int = 50,
        offset: int = 0,
    ) -> VkApiRequest:
        """
        Builds a request to search for playlists by text.

        Args:
            text (str): The text.
            count (int): The number of playlists. (default 50)
            offset (int): The offset. (default 0)
        """
        params: Dict = {
            "q": text,
            "count": count,
            "offset": offset,
        }

        return cls.build_from_base_request(
            method="get", url="audio.searchPlaylists", params=params
        )

    @classmethod
    def build_req_search_albums(
        cls,
        text: str,
        count: int = 50,
        offset: int = 0,
    ) -> VkApiRequest:
        """
        Builds a request to search for albums by text.

        Args:
            text (str): The text.
            count (int): The number of albums. (default 50)
            offset (int): The offset. (default 0)
        """
        params: Dict = {
            "q": text,
            "count": count,
            "offset": offset,
        }

        return cls.build_from_base_request(
            method="get", url="audio.searchAlbums", params=params
        )

    @classmethod
    def build_req_get_popular(
        cls,
        count: int = 500,
        offset: int = 0,
    ) -> VkApiRequest:
        """
        Builds a request to get popular audio.

        Args:
            count (int): The number of audio recordings. (default 500)
            offset (int): The offset. (default 0)
        """
        params: Dict = {
            "count": count,
            "offset": offset,
        }

        return cls.build_from_base_request(
            method="get", url="audio.getPopular", params=params
        )

    @classmethod
    def build_req_get_recommendations(
        cls,
        user_id: Optional[int] = None,
        song_id: Optional[int] = None,
        count: int = 100,
        offset: int = 0,
    ) -> VkApiRequest:
        """
        Builds a request to get audio recommendations.

        Args:
            user_id (int): The user ID for which recommendations are being received. (default None)
            song_id (int): The song ID for which recommendations are being received. (default None)
            count (int): The number of audio recordings. (default 100)
            offset (int): The offset. (default 0)
        """
        params: Dict = {
            "count": count,
            "offset": offset,
        }

        if user_id:
            params["user_id"] = user_id

        if song_id:
            params["target_id"] = song_id

        return cls.build_from_base_request(
            method="get", url="audio.getRecommendations", params=params
        )
