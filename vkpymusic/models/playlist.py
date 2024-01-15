"""
This module contains the Playlist class.
"""


class Playlist:
    """
    A class that represents a playlist.

    Attributes:
        title (str): The title of the playlist.
        description (str): The description of the playlist.
        photo (str): The URL of the playlist's photo.
        count (int): The number of tracks in the playlist.
        owner_id (int): The ID of the playlist's owner.
        playlist_id (int): The ID of the playlist.
        access_key (str): The access key of the playlist.
    """

    title: str
    description: str
    photo: str
    count: int
    followers: int
    owner_id: int
    playlist_id: int
    access_key: str

    def __init__(
        self,
        title: str,
        description: str,
        photo: str,
        count: int,
        followers: int,
        owner_id: int,
        playlist_id: int,
        access_key: str,
    ) -> None:
        """
        Initializes a Playlist object.

        Args:
            title (str): The title of the playlist.
            description (str): The description of the playlist.
            photo (str): The URL of the playlist's photo.
            count (int): The number of tracks in the playlist.
            owner_id (int): The ID of the playlist's owner.
            playlist_id (int): The ID of the playlist.
            access_key (str): The access key of the playlist.
        """
        self.title = title
        self.description = description
        self.photo = photo
        self.count = count
        self.followers = followers
        self.owner_id = owner_id
        self.playlist_id = playlist_id
        self.access_key = access_key

    def __str__(self):
        return f"{self.title} ({self.count} tracks)"

    def to_dict(self) -> dict:
        """
        Converts the playlist to a dictionary.

        Returns:
            dict: The playlist as a dictionary.
        """
        return self.__dict__

    @classmethod
    def from_json(cls, item) -> "Playlist":
        """
        Converts a JSON object to a Playlist object.

        Args:
            item (dict): A JSON object.

        Returns:
            Playlist: The Playlist object.
        """
        title = str(item["title"])
        description = str(item["description"])
        if "photo" in item:
            photo = str(item["photo"]["photo_1200"])
        else:
            photo = ""
        count = int(item["count"])
        followers = int(item["followers"])
        owner_id = int(item["owner_id"])
        playlist_id = int(item["id"])
        access_key = str(item["access_key"])
        playlist = cls(
            title,
            description,
            photo,
            count,
            followers,
            owner_id,
            playlist_id,
            access_key,
        )
        return playlist
