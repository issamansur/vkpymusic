"""
VKpyMusic
~~~~~~~~~

A library for interacting with music in VK.

Provides a convenient API for authorization, 
receiving audio recordings, searching for music,
as well as downloading individual songs and 
playlists of the user in VK.

:copyright: (c) 2023-present issamansur (EDEXADE, inc)
:license: MIT, see LICENSE for more details.
"""

__title__ = "vkpymusic"
__author__ = "issamansur"
__license__ = "MIT"
__copyright__ = "Copyright 2023-present issamansur (EDEXADE, inc)"
__version__ = "3.0.1"

from .client import Client, clients
from .token_receiver import TokenReceiver
from .token_receiver_async import TokenReceiverAsync
from .service import Service
from .service_async import ServiceAsync
from .song import Song
from .playlist import Playlist

from . import utils

__all__ = [
    "Client",
    "clients",
    "TokenReceiver",
    "TokenReceiverAsync",
    "Service",
    "ServiceAsync",
    "Song",
    "Playlist",
    "utils",
]
