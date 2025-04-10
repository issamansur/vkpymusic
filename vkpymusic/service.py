"""
This module contains the main class 'Service' for working with VK API.
"""

import os
import configparser
import logging
from typing import Optional, Union, List

import aiofiles
from httpx import Client, AsyncClient, Response

from .vk_api import (
    VkApiRequestBuilder, 
    VkApiRequest, 
    VkApiResponse, 
    VkApiException,

    make_request,
    make_request_async,
)
from .models import Song, Playlist, UserInfo
from .utils import Converter, create_logger


class Service:
    """
    A class for working with VK API.

    Attributes:
        user_agent (str): User agent string.
        __token (str):    Token for VK API.
        logger (logging.Logger): The logger for class.

    Example usage:
    ```
    >>> service = Service.parse_config()
    >>> songs = service.search_songs_by_text("Imagine Dragons")
    >>> for song in songs:
    ...     Service.save_music(song)
    >>> // or
    >>> songs = await service.search_songs_by_text_async("Imagine Dragons")
    >>> for song in songs:
    ...     await Service.save_music_async(song)
    ```
    """

    logger: logging.Logger = create_logger(__name__)

    #############
    # CONSTRUCTOR
    def __init__(self, user_agent: str, token: str) -> None:
        """
        Initializes a Service object.

        Args:
            user_agent (str): User agent string.
            token (str):      Token for VK API.
        """
        self.user_agent = user_agent
        self.__token = token

    @classmethod
    def set_logger(cls, logger: logging.Logger) -> None:
        """
        Set logger for class.

        Args:
            logger (logging.Logger): Logger.
        """
        cls.logger = logger

    ##################################
    # METHODS WITH WORKING WITH CONFIG
    @classmethod
    def parse_config(cls, filename: str = "config_vk.ini"):
        """
        Create an instance of Service from config created by 'TokenReceiver'.

        Args:
            filename (str): Filename of config (default = "config_vk.ini").
        """
        dirname = os.path.dirname(__file__)
        configfile_path = os.path.join(dirname, filename)
        try:
            config = configparser.ConfigParser()
            config.read(configfile_path, encoding="utf-8")
            user_agent = config["VK"]["user_agent"]
            token = config["VK"]["token_for_audio"]
            return cls(user_agent, token)
        except Exception as e:
            cls.logger.error("Config not found or invalid: " + str(e))

    def del_config(cls, filename: str = "config_vk.ini"):
        """
        Delete config created by 'TokenReceiver'.

        Args:
            filename (str): Filename of config (default value = "config_vk.ini").
        """
        configfile_path = os.path.join(os.path.dirname(__file__), filename)
        try:
            os.remove(configfile_path)
            cls.logger.info("Config successful deleted!")
        except Exception as e:
            cls.logger.warning(e)

    ####################################
    # METHODS FOR REQUESTS WITH HANDLERS
    def fill_user_agent_and_token(self, request: VkApiRequest) -> None:
        """
        Fill user-agent and token in request.

        Args:
            request (VkApiRequest): Request to fill.
        """
        request.fill_token(self.__token)
        request.fill_user_agent(self.user_agent)

    ##############################################
    # METHODS FOR WORKING WITH TOKEN AND USER INFO
    def get_user_info(self) -> UserInfo:
        """
        Get user info by token (sync).

        Returns:
            UserInfo: Instance of 'UserInfo'.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info("Getting user info...")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_profile_info()
        request.fill_token(self.__token)
        response: VkApiResponse = make_request(request)
        user_info: UserInfo = Converter.response_to_userinfo(response)
        self.logger.info(f"User info: {user_info}")
        return user_info

    async def get_user_info_async(self) -> UserInfo:
        """
        Get user info by token (async).

        Returns:
            UserInfo: Instance of 'UserInfo'.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info("Getting user info...")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_profile_info()
        request.fill_token(self.__token)
        response: VkApiResponse = await make_request_async(request)
        user_info: UserInfo = Converter.response_to_userinfo(response)
        self.logger.info(f"User info: {user_info}")
        return user_info

    @classmethod
    def check_token(cls, token: str) -> bool:
        """
        Check token for VK API (sync).

        Args:
            token (str): Token for VK API.

        Returns:
            bool: True if token is valid, False otherwise.
        """
        cls.logger.info("Checking token...")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_profile_info()
        request.fill_token(token)
        try:
            make_request(request)
            cls.logger.info("Token is valid!")
            return True
        except VkApiException as e:
            cls.logger.info("Token is invalid!")
            return False

    @classmethod
    async def check_token_async(cls, token: str) -> bool:
        """
        Check token for VK API (async).

        Args:
            token (str): Token for VK API.

        Returns:
            bool: True if token is valid, False otherwise.
        """
        cls.logger.info("Checking token...")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_profile_info()
        request.fill_token(token)
        try:
            await make_request_async(request)
            cls.logger.info("Token is valid!")
            return True
        except VkApiException as e:
            cls.logger.info("Token is invalid!")
            return False

    def is_token_valid(self) -> bool:
        """
        Check token for VK API (sync).

        Returns:
            bool: True if token is valid, False otherwise.
        """
        return self.check_token(self.__token)

    async def is_token_valid_async(self) -> bool:
        """
        Check token for VK API (async).

        Returns:
            bool: True if token is valid, False otherwise.
        """
        return await self.check_token_async(self.__token)

    ################################
    # METHODS FOR WORKING WITH AUDIO

    # Count of songs section
    def get_count_by_user_id(self, user_id: Union[str, int]) -> int:
        """
        Get count of all user's songs (sync).

        Args:
            user_id (str | int): VK user id. (NOT USERNAME! vk.com/id*******).

        Returns:
            int: count of all user's songs or -1 if access denied.

        Raises:
            VkApiException: If the response contains an error.
        """
        user_id = int(user_id)
        self.logger.info(f"Request by user: {user_id}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_count(user_id)
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = make_request(request)
        songs_count: int = response.data
        self.logger.info(f"Count of user's songs: {songs_count}")

        if songs_count != 0:
            return songs_count

        # If count of songs is 0, it can be due to access
        # denied to user's songs. So check this case.
        self.logger.info(f"Trying to get songs by user id: {user_id}")
        try:
            self.get_songs_by_userid(user_id, 1)
            return songs_count
        except VkApiException as e:
            # If error code is 201, it means access denied to user's songs.
            if e.error_code == 201:
                self.logger.warning(
                    f"Access denied to user's songs."
                )
                return -1
            raise

    async def get_count_by_user_id_async(self, user_id: Union[str, int]) -> int:
        """
        Get count of all user's songs (async).

        Args:
            user_id (str | int): VK user id. (NOT USERNAME! vk.com/id*******).

        Returns:
            int: count of all user's songs or -1 if access denied.

        Raises:
            VkApiException: If the response contains an error.
        """
        user_id = int(user_id)
        self.logger.info(f"Request by user: {user_id}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_count(user_id)
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = await make_request_async(request)
        songs_count: int = response.data
        self.logger.info(f"Count of user's songs: {songs_count}")

        if songs_count != 0:
            return songs_count

        # If count of songs is 0, it can be due to access
        # denied to user's songs. So check this case.
        self.logger.info(f"Trying to get songs by user id: {user_id}")
        try:
            await self.get_songs_by_userid_async(user_id, 1)
            return songs_count
        except VkApiException as e:
            # If error code is 201, it means access denied to user's songs.
            if e.error_code == 201:
                self.logger.warning(
                    f"Access denied to user's songs."
                )
                return -1
            raise

    # Songs section
    def get_songs_by_userid(
        self, user_id: Union[str, int], count: int = 100, offset: int = 0
    ) -> List[Song]:
        """
        Search songs by owner/user id (sync).

        Args:
            user_id (str | int): VK user id. (NOT USERNAME! vk.com/id*******).
            count (int):          Count of resulting songs (for VK API: default/max = 100).
            offset (int):         Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        user_id = int(user_id)
        self.logger.info(f"Request by user: {user_id}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get(
            user_id, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = make_request(request)
        songs: List[Song] = Converter.response_to_songs(response)
        if len(songs) == 0:
            self.logger.info("No results found ._.")
        else:
            self.logger.info(f"Found {len(songs)} songs")
        return songs

    async def get_songs_by_userid_async(
        self, user_id: Union[str, int], count: int = 100, offset: int = 0
    ) -> List[Song]:
        """
        Search songs by owner/user id (async).

        Args:
            user_id (str | int): VK user id. (NOT USERNAME! vk.com/id*******).
            count (int):          Count of resulting songs (for VK API: default/max = 100).
            offset (int):         Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        user_id = int(user_id)
        self.logger.info(f"Request by user: {user_id}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get(
            user_id, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = await make_request_async(request)
        songs: List[Song] = Converter.response_to_songs(response)
        if len(songs) == 0:
            self.logger.info("No results found ._.")
        else:
            self.logger.info(f"Found {len(songs)} songs")
        return songs

    def get_songs_by_playlist_id(
        self,
        user_id: Union[str, int],
        playlist_id: int,
        access_key: str,
        count: int = 100,
        offset: int = 0,
    ) -> List[Song]:
        """
        Get songs by playlist id (sync).

        Args:
            user_id (str | int): VK user id. (NOT USERNAME! vk.com/id*******).
            playlist_id (int):    VK playlist id. (Take it from methods for playlist).
            access_key (str):     VK access key. (Take it from methods for playlist).
            count (int):          Count of resulting songs (for VK API: default/max = 100).
            offset (int):         Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        user_id = int(user_id)
        self.logger.info(f"Request by user: {user_id}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get(
            user_id, count, offset, playlist_id, access_key
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = make_request(request)
        songs: List[Song] = Converter.response_to_songs(response)
        if len(songs) == 0:
            self.logger.info("No results found ._.")
        else:
            self.logger.info(f"Found {len(songs)} songs")
        return songs

    async def get_songs_by_playlist_id_async(
        self,
        user_id: Union[str, int],
        playlist_id: int,
        access_key: str,
        count: int = 100,
        offset: int = 0,
    ) -> List[Song]:
        """
        Get songs by playlist id (async).

        Args:
            user_id (str | int): VK user id. (NOT USERNAME! vk.com/id*******).
            playlist_id (int):    VK playlist id. (Take it from methods for playlist).
            access_key (str):     VK access key. (Take it from methods for playlist).
            count (int):          Count of resulting songs (for VK API: default/max = 100).
            offset (int):         Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        user_id = int(user_id)
        self.logger.info(f"Request by user: {user_id}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get(
            user_id, count, offset, playlist_id, access_key
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = await make_request_async(request)
        songs: List[Song] = Converter.response_to_songs(response)
        if len(songs) == 0:
            self.logger.info("No results found ._.")
        else:
            self.logger.info(f"Found {len(songs)} songs")
        return songs

    def get_songs_by_playlist(
        self, playlist: Playlist, count: int = 10, offset: int = 0
    ) -> List[Song]:
        """
        Get songs by instance of 'Playlist' (sync).

        Args:
            playlist (Playlist): Instance of 'Playlist' (take from methods for receiving Playlist).
            count (int):         Count of resulting songs (for VK API: default/max = 100).
            offset (int):        Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info(f"Request by playlist: {playlist}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get(
            playlist.owner_id, count, offset, playlist.playlist_id, playlist.access_key
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = make_request(request)
        songs: List[Song] = Converter.response_to_songs(response)
        if len(songs) == 0:
            self.logger.info("No results found ._.")
        else:
            self.logger.info(f"Found {len(songs)} songs")
        return songs

    async def get_songs_by_playlist_async(
        self, playlist: Playlist, count: int = 10, offset: int = 0
    ) -> List[Song]:
        """
        Get songs by instance of 'Playlist' (async).

        Args:
            playlist (Playlist): Instance of 'Playlist' (take from methods for receiving Playlist).
            count (int):         Count of resulting songs (for VK API: default/max = 100).
            offset (int):        Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info(f"Request by playlist: {playlist}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get(
            playlist.owner_id, count, offset, playlist.playlist_id, playlist.access_key
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = await make_request_async(request)
        songs: List[Song] = Converter.response_to_songs(response)
        if len(songs) == 0:
            self.logger.info("No results found ._.")
        else:
            self.logger.info(f"Found {len(songs)} songs")
        return songs

    def search_songs_by_text(
        self, text: str, count: int = 3, offset: int = 0
    ) -> List[Song]:
        """
        Search songs by text/query (sync).

        Args:
            text (str):   Text of query. Can be title of song, author, etc.
            count (int):  Count of resulting songs (for VK API: default/max = 100).
            offset (int): Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info(f'Request by text: "{text}" в количестве {count}')
        request: VkApiRequest = VkApiRequestBuilder.build_req_search(
            text, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = make_request(request)
        songs: List[Song] = Converter.response_to_songs(response)
        if len(songs) == 0:
            self.logger.info("No results found ._.")
        else:
            self.logger.info(f"Found {len(songs)} songs")
        return songs

    async def search_songs_by_text_async(
        self, text: str, count: int = 3, offset: int = 0
    ) -> List[Song]:
        """
        Search songs by text/query (async).

        Args:
            text (str):   Text of query. Can be title of song, author, etc.
            count (int):  Count of resulting songs (for VK API: default/max = 100).
            offset (int): Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info(f'Request by text: "{text}" в количестве {count}')
        request: VkApiRequest = VkApiRequestBuilder.build_req_search(
            text, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = await make_request_async(request)
        songs: List[Song] = Converter.response_to_songs(response)
        if len(songs) == 0:
            self.logger.info("No results found ._.")
        else:
            self.logger.info(f"Found {len(songs)} songs")
        return songs

    # Playlists and albums section
    def get_playlists_by_userid(
        self, user_id: Union[str, int], count: int = 5, offset: int = 0
    ) -> List[Playlist]:
        """
        Get playlist by owner/user id (sync).

        Args:
            user_id (str or int): VK user id. (NOT USERNAME! vk.com/id*******).
            count (int):          Count of resulting playlists (for VK API: default = 50, max = 100).
            offset (int):         Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Playlist]: List of playlists.
        
        Raises:
            VkApiException: If the response contains an error.
        """
        user_id = int(user_id)
        self.logger.info(f"Request by user: {user_id}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_playlists(
            user_id, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = make_request(request)
        playlists: List[Playlist] = Converter.response_to_playlists(response)
        return playlists
    
    async def get_playlists_by_userid_async(
        self, user_id: Union[str, int], count: int = 5, offset: int = 0
    ) -> List[Playlist]:
        """
        Get playlist by owner/user id (async).

        Args:
            user_id (str or int): VK user id. (NOT USERNAME! vk.com/id*******).
            count (int):          Count of resulting playlists (for VK API: default = 50, max = 100).
            offset (int):         Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Playlist]: List of playlists.
        
        Raises:
            VkApiException: If the response contains an error.
        """
        user_id = int(user_id)
        self.logger.info(f"Request by user: {user_id}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_playlists(
            user_id, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = await make_request_async(request)
        playlists: List[Playlist] = Converter.response_to_playlists(response)
        return playlists

    def search_playlists_by_text(
        self, text: str, count: int = 5, offset: int = 0
    ) -> List[Playlist]:
        """
        Search playlists by text/query (sync).
        Playlist - it user's collection of songs.

        Args:
            text (str):   Text of query. Can be title of playlist, genre, etc.
            count (int):  Count of resulting playlists (for VK API: default = 50, max = 100).
            offset (int): Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Playlist]: List of playlists.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info(f"Request by text: {text}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_search_playlists(
            text, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = make_request(request)
        playlists: List[Playlist] = Converter.response_to_playlists(response)
        return playlists

    async def search_playlists_by_text_async(
        self, text: str, count: int = 5, offset: int = 0
    ) -> List[Playlist]:
        """
        Search playlists by text/query (async).
        Playlist - it user's collection of songs.

        Args:
            text (str):   Text of query. Can be title of playlist, genre, etc.
            count (int):  Count of resulting playlists (for VK API: default = 50, max = 100).
            offset (int): Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Playlist]: List of playlists.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info(f"Request by text: {text}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_search_playlists(
            text, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = await make_request_async(request)
        playlists: List[Playlist] = Converter.response_to_playlists(response)
        return playlists

    def search_albums_by_text(
        self, text: str, count: int = 5, offset: int = 0
    ) -> List[Playlist]:
        """
        Search albums by text/query (sync).
        Album - artists' album/collection of songs.
        In obj context - same as 'Playlist'.

        Args:
            text (str):   Text of query. Can be title of album, name of artist, etc.
            count (int):  Count of resulting playlists (for VK API: default = 50, max = 100).
            offset (int): Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Playlist]: List of albums.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info(f"Request by text: {text}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_search_albums(
            text, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = make_request(request)
        playlists: List[Playlist] = Converter.response_to_playlists(response)
        return playlists
    
    async def search_albums_by_text_async(
        self, text: str, count: int = 5, offset: int = 0
    ) -> List[Playlist]:
        """
        Search albums by text/query (async).
        Album - artists' album/collection of songs.
        In obj context - same as 'Playlist'.

        Args:
            text (str):   Text of query. Can be title of album, name of artist, etc.
            count (int):  Count of resulting playlists (for VK API: default = 50, max = 100).
            offset (int): Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Playlist]: List of albums.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info(f"Request by text: {text}")
        request: VkApiRequest = VkApiRequestBuilder.build_req_search_albums(
            text, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = await make_request_async(request)
        playlists: List[Playlist] = Converter.response_to_playlists(response)
        return playlists

    # Popular and recommendations section
    def get_popular(self, count: int = 50, offset: int = 0) -> List[Song]:
        """
        Get popular songs (sync). (Be careful, it always returns less than count)

        Args:
            count (int):  Count of resulting songs (for VK API: default = 50, max = 500).
            offset (int): Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info("Request popular songs")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_popular(count, offset)
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = make_request(request)
        songs: List[Song] = Converter.response_to_popular(response)
        return songs

    async def get_popular_async(self, count: int = 50, offset: int = 0) -> List[Song]:
        """
        Get popular songs (async). (Be careful, it always returns less than count)

        Args:
            count (int):  Count of resulting songs (for VK API: default = 50, max = 500).
            offset (int): Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info("Request popular songs")
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_popular(count, offset)
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = await make_request_async(request)
        songs: List[Song] = Converter.response_to_popular(response)
        return songs

    # TODO
    def get_recommendations(
        self,
        user_id: Optional[Union[str, int]] = None,
        song_id: Optional[Union[str, int]] = None,
        count: int = 50,
        offset: int = 0,
    ) -> List[Song]:
        """
        Get recommendations by user id or song id (sync). (Be careful, it always returns less than count)

        Args:
            user_id (int):  VK user id. (NOT USERNAME! vk.com/id*******).
            song_id (int):  VK song id.
            count (int):    Count of resulting songs (for VK API: default = 50, max = 300).
            offset (int):   Set offset for result. For example, count = 100, offset = 100 -> 101-200.

        Returns:
            list[Song]: List of songs.

        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info(
            f"Request recommendations by user id: {user_id or '[NOT SET]'} and song id: {song_id or '[NOT SET]'}"
        )
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_recommendations(
            user_id, song_id, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = make_request(request)
        songs: List[Song] = Converter.response_to_songs(response)
        return songs
    
    async def get_recommendations_async(
        self,
        user_id: Optional[Union[str, int]] = None,
        song_id: Optional[Union[str, int]] = None,
        count: int = 50,
        offset: int = 0,
    ) -> List[Song]:
        """
        Get recommendations by user id or song id (async). (Be careful, it always returns less than count)

        Args:
            user_id (int):  VK user id. (NOT USERNAME! vk.com/id*******).
            song_id (int):  VK song id.
            count (int):    Count of resulting songs (for VK API: default = 50, max = 300).
            offset (int):   Set offset for result. For example, count = 100, offset = 100 -> 101-200.
        
        Returns:
            list[Song]: List of songs.
        
        Raises:
            VkApiException: If the response contains an error.
        """
        self.logger.info(
            f"Request recommendations by user id: {user_id or '[NOT SET]'} and song id: {song_id or '[NOT SET]'}"
        )
        request: VkApiRequest = VkApiRequestBuilder.build_req_get_recommendations(
            user_id, song_id, count, offset
        )
        self.fill_user_agent_and_token(request)
        response: VkApiResponse = await make_request_async(request)
        songs: List[Song] = Converter.response_to_songs(response)
        return songs

    ################
    # EXTENSION METHODS
    @classmethod
    def save_music(cls, song: Song, overwrite: bool = False) -> Optional[str]:
        """
        Save song (sync) to '{workDirectory}/Music/{song name}.mp3'.
        If you wanna another behavior, you can override this method
        or use your own method for saving music.

        Args:
            song (Song): 'Song' instance obtained from 'Service' methods.
            overwrite (bool): If True, overwrite file if it exists. By default doesn't overwrite.

        Returns:
            str: relative path of downloaded music or None if error.
        """
        song.to_safe()
        file_name_mp3 = f"{song}.mp3"
        url = song.url
        if not url:
            cls.logger.warning("Url no found")
            return None
        elif "index.m3u8" in url:
            cls.logger.error(".m3u8 detected!")
            return None

        try:
            with Client() as client:
                response: Response = client.get(url)

            if response.status_code != 200:
                cls.logger.error(f"Error while downloading {song}: {response.status_code}")
                return None
        except Exception as e:
            cls.logger.error(f"Error while downloading {song}: {e}")
            return None

        music_dir: str = os.path.join(os.getcwd(), "Music")
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
            cls.logger.info("Folder 'Music' was created")

        file_path: str = os.path.join(music_dir, file_name_mp3)
        if os.path.exists(file_path):
            cls.logger.info(
                f"File with name {file_name_mp3} already exists."
            )
            if overwrite:
                cls.logger.info("File will be overwritten")
            else:
                cls.logger.info("File will not be overwritten")
                return file_path

        cls.logger.info(f"Downloading {song}...")

        try:
            with open(file_path, "wb") as output_file:
                output_file.write(response.content)
            cls.logger.info(f"Success! Music was downloaded in '{file_path}'")
            return file_path
        except Exception as e:
            cls.logger.error(f"Error while saving {song}: {e}")
            return None

    @classmethod
    async def save_music_async(cls, song: Song, overwrite: bool = False) -> Optional[str]:
        """
        Save song (async) to '{workDirectory}/Music/{song name}.mp3'.
        If you wanna another behavior, you can override this method
        or use your own method for saving music.

        Args:
            song (Song): 'Song' instance obtained from 'Service' methods.
            overwrite (bool): If True, overwrite file if it exists. By default doesn't overwrite.

        Returns:
            str: relative path of downloaded music or None if error.
        """
        song.to_safe()
        file_name_mp3 = f"{song}.mp3"
        url = song.url
        if not url:
            cls.logger.warning("Url no found")
            return None
        elif "index.m3u8" in url:
            cls.logger.error(".m3u8 detected!")
            return None

        try:
            async with AsyncClient() as client:
                response: Response = await client.get(url)

            if response.status_code != 200:
                cls.logger.error(f"Error while downloading {song}: {response.status_code}")
                return None
        except Exception as e:
            cls.logger.error(f"Error while downloading {song}: {e}")
            return None

        music_dir: str = os.path.join(os.getcwd(), "Music")
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
            cls.logger.info("Folder 'Music' was created")

        file_path: str = os.path.join(music_dir, file_name_mp3)
        if os.path.exists(file_path):
            cls.logger.info(
                f"File with name {file_name_mp3} already exists."
            )
            if overwrite:
                cls.logger.info("File will be overwritten")
            else:
                cls.logger.info("File will not be overwritten")
                return file_path

        cls.logger.info(f"Downloading {song}...")

        try:
            async with aiofiles.open(file_path, "wb") as output_file:
                await output_file.write(response.content)
            cls.logger.info(f"Success! Music was downloaded in '{file_path}'")
            return file_path
        except Exception as e:
            cls.logger.error(f"Error while saving {song}: {e}")
            return None