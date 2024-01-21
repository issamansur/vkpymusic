"""
This module contains all models for vkpymusic.

Classes:
    Song: A class that represents a song.
    Playlist: A class that represents a playlist.
    UserInfo: A class that represents a main user's info.
"""

from .song import Song
from .playlist import Playlist
from .userinfo import UserInfo

__all__ = [
    "Song",
    "Playlist",
    "UserInfo",
]
