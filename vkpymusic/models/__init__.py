"""
This module contains all models for vkpymusic.

Classes:
    Song: A class that represents a song.
    Playlist: A class that represents a playlist.
"""

from .song import Song
from .playlist import Playlist

__all__ = [
    "Song",
    "Playlist",
]
