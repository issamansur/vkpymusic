"""
This module contains the Song class.
"""

import re


class Song:
    """
    A class that represents a song.

    Attributes:
        title (str): The title of the song.
        artist (str): The artist of the song.
        duration (int): The duration of the song in seconds.
        track_id (str): The ID of the song.
        owner_id (str): The ID of the song's owner.
        url (str): The URL of the song.
    """

    title: str
    artist: str
    duration: int
    track_id: str
    owner_id: str
    url: str

    def __init__(
        self,
        title: str,
        artist: str,
        duration: int,
        track_id: str,
        owner_id: str,
        url: str = "",
    ) -> None:
        """
        Initializes a Song object.

        Args:
            title (str): The title of the song.
            artist (str): The artist of the song.
            duration (int): The duration of the song in seconds.
            track_id (str): The ID of the song.
            owner_id (str): The ID of the song's owner.
            url (str): The URL of the song.
        """
        self.title = title
        self.artist = artist
        self.duration = duration
        self.track_id = track_id
        self.owner_id = owner_id
        self.url = url

    def __str__(self):
        return f"{self.title} - {self.artist}"

    def to_dict(self) -> dict:
        """
        Converts the song to a dictionary.

        Returns:
            dict: The song as a dictionary.
        """
        return self.__dict__

    def to_safe(self):
        """
        Removes all non-alphanumeric characters from the song's title and artist.
        """

        def safe_format(string):
            safe_string = re.sub(r"[^A-zА-я0-9+\s]", "", string)
            return safe_string

        self.title = safe_format(self.title)
        self.artist = safe_format(self.artist)

    @classmethod
    def from_json(cls, item) -> "Song":
        """
        Creates a Song object from a JSON object.

        Args:
            item (dict): A JSON object.

        Returns:
            Song: A Song object.
        """
        title = str(item["title"])
        artist = str(item["artist"])
        duration = int(item["duration"])
        track_id = str(item["id"])
        owner_id = str(item["owner_id"])
        url = str(item["url"])
        song = cls(title, artist, duration, track_id, owner_id, url)
        return song
