"""
VKpyMusic
=========
A library for interacting with music in VK.

Provides a convenient API for authorization, 
receiving audio recordings, searching for music,
as well as downloading individual songs and 
playlists of the user in VK.

Classes:
    Client: A class that stores the user agent string, client ID, and client secret.
    TokenReceiver: A class for receiving an access token.
    Service: A class for interacting with VK API.

Modules:
    models: A module that contains all models for vkpymusic.
    utils: A module that contains utilities for conversion and logging.
    vk_api: A module that contains classes for requests to VK API.
"""

__title__ = "vkpymusic"
__author__ = "issamansur"
__license__ = "MIT"
__copyright__ = "Copyright 2023-present issamansur (EDEXADE, Inc)"
__version__ = "3.5.1"

from .client import Client, clients
from .token_receiver import TokenReceiver
from .service import Service

from . import vk_api, models, utils

__all__ = [
    "Client",
    "clients",
    "TokenReceiver",
    "Service",
    "vk_api",
    "models",
    "utils",
]
