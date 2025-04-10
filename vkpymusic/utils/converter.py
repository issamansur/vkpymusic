"""
This module contains the Converter class.
"""

from typing import List

from ..vk_api import VkApiResponse
from ..models import Song, Playlist, UserInfo


class Converter:
    """
    A class that converts a response from VK to a list of songs or playlists.
    """

    @staticmethod
    def response_to_songs(response: VkApiResponse) -> List[Song]:
        """
        Converts a response to a list of songs.

        Args:
            response (VkApiResponse): The response object from VK.

        Returns:
            List[Song]: A list of songs converted from the response.
        """
        items: List[dict] = response.data.get("items", [])

        songs: List[Song] = []
        for item in items:
            song = Song.from_json(item)
            songs.append(song)
        return songs

    @staticmethod
    def response_to_playlists(response: VkApiResponse) -> List[Playlist]:
        """
        Converts a response to a list of playlists.

        Args:
            response (VkApiResponse): The response object from VK.

        Returns:
            List[Playlist]: A list of playlists converted from the response.
        """
        items: List[dict] = response.data.get("items", [])

        playlists: List[Playlist] = []
        for item in items:
            playlist = Playlist.from_json(item)
            playlists.append(playlist)

        return playlists

    @staticmethod
    def response_to_userinfo(response: VkApiResponse) -> UserInfo:
        """
        Converts a response to a UserInfo.

        Args:
            response (VkApiResponse): The response object from VK.

        Returns:
            UserInfo: A UserInfo converted from the response.
        """
        userinfo: UserInfo = UserInfo.from_json(response.data)

        return userinfo

    @staticmethod
    def response_to_popular(response: VkApiResponse) -> List[Song]:
        """
        Converts a response to a list of POPULAR songs.

        Args:
            response (VkApiResponse): The response object from VK.

        Returns:
            List[Song]: A list of songs converted from the response.
        """
        songs: List[Song] = []
        for item in response.data:
            song = Song.from_json(item)
            songs.append(song)

        return songs