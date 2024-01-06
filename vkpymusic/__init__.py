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
    TokenReceiverAsync: A class for receiving an access token asynchronously.
    Service: A class for interacting with VK API.
    ServiceAsync: A class for interacting with VK API asynchronously.

Modules:
    models: A module that contains all models for vkpymusic.
    utils: A module that contains utilities for conversion and logging.
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

from . import models
from . import utils

__all__ = [
    "Client",
    "clients",
    "TokenReceiver",
    "TokenReceiverAsync",
    "Service",
    "ServiceAsync",
    "models",
    "utils",
]
