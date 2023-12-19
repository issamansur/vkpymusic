import json
import logging
from typing import List

from requests import Response

from ..song import Song
from ..playlist import Playlist
from .logger import get_logger


logger: logging.Logger = get_logger(__name__)

class Converter:
    @staticmethod
    def response_to_songs(response: Response):
        response = json.loads(response.content.decode("utf-8"))
        try:
            items = response["response"]["items"]
        except Exception as e:
            logger.error(e)
        songs: List[Song] = []
        for item in items:
            song = Song.from_json(item)
            songs.append(song)
        return songs

    @staticmethod
    def response_to_playlists(response: Response):
        response = json.loads(response.content.decode("utf-8"))
        try:
            items = response["response"]["items"]
        except Exception as e:
            logger.error(e)
        playlists: List[Playlist] = []
        for item in items:
            playlist = Playlist.from_json(item)
            playlists.append(playlist)
        return playlists
