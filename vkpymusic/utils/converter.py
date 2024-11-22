"""
This module contains the Converter class.
"""

import json
import logging
from typing import List, Optional

from requests import Response

from ..models import Song, Playlist, UserInfo


class Converter:
    """
    A class that converts a response from VK to a list of songs or playlists.
    """

    @staticmethod
    def response_to_songs(response: Response) -> List[Song]:
        """
        Converts a response to a list of songs.

        Args:
            response (Response): The response object from VK.

        Returns:
            List[Song]: A list of songs converted from the response.
        """
        response = json.loads(response.content.decode("utf-8"))
        items = response["response"]["items"]

        songs: List[Song] = []
        for item in items:
            song = Song.from_json(item)
            songs.append(song)
        return songs

    @staticmethod
    def response_to_playlists(response: Response) -> List[Playlist]:
        """
        Converts a response to a list of playlists.

        Args:
            response (Response): The response object from VK.

        Returns:
            List[Playlist]: A list of playlists converted from the response.
        """
        response = json.loads(response.content.decode("utf-8"))
        items = response["response"]["items"]

        playlists: List[Playlist] = []
        for item in items:
            playlist = Playlist.from_json(item)
            playlists.append(playlist)

        return playlists

    @staticmethod
    def response_to_userinfo(response: Response) -> Optional[UserInfo]:
        """
        Converts a response to a UserInfo.

        Args:
            response (Response): The response object from VK.

        Returns:
            UserInfo: A UserInfo converted from the response.
        """
        response = json.loads(response.content.decode("utf-8"))
        item = response["response"]
        userinfo: UserInfo = UserInfo.from_json(item)

        return userinfo

    @staticmethod
    def response_to_popular(response: Response) -> List[Song]:
        """
        Converts a response to a list of POPULAR songs.

        Args:
            response (Response): The response object from VK.

        Returns:
            List[Song]: A list of songs converted from the response.
        """
        response = json.loads(response.content.decode("utf-8"))
        items = response["response"]

        songs: List[Song] = []
        for item in items:
            song = Song.from_json(item)
            songs.append(song)

        return songs