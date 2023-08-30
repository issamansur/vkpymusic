class Playlist:
    def __init__(self, title, count, owner_id, playlist_id, access_key):
        self.title = title
        self.count = count
        self.owner_id = owner_id
        self.playlist_id = playlist_id
        self.access_key = access_key


    def __str__(self):
        return f"{self.title} ({self.count} tracks)"

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def from_json(cls, item):
        title = str(item["title"])
        count = int(item["count"])
        owner_id = int(item["owner_id"])
        playlist_id = int(item["id"])
        access_key = str(item["access_key"])

        playlist = cls(title, count, owner_id, playlist_id, access_key)
        return playlist