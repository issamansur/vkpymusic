import re


class Music:
    def __init__(self, title, artist, duration, track_id, owner_id, url=""):
        self.title = title
        self.artist = artist
        self.duration = duration
        self.track_id = track_id
        self.owner_id = owner_id
        self.url = url

    def __str__(self):
        return f"{self.title} - {self.artist}"

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def safe(cls, music):
        def safe_format(string):
            safe_string = re.sub(r"[^A-zА-я0-9+\s]", "", string)
            return safe_string

        title = safe_format(music.title)
        artist = safe_format(music.artist)
        safeMusic = cls(
            title, artist, music.duration, music.track_id, music.owner_id, music.url
        )
        return safeMusic

    @classmethod
    def from_json(cls, item):
        title = str(item["title"])
        artist = str(item["artist"])
        duration = int(item["duration"])
        track_id = str(item["id"])
        owner_id = str(item["owner_id"])
        url = str(item["url"])

        music = cls(title, artist, duration, track_id, owner_id, url)
        return music
