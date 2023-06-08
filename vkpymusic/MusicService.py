import os, configparser
import requests, json

from .Music import Music


def log(message):
    print(f"[vkpymusic -> Service]: {message}")


class Service:
    def __init__(self, user_agent: str, token: str):
        self.user_agent = user_agent
        self.__token = token

    @classmethod
    def parse_config(cls, filename: str = "config_vk.ini"):
        """
        Create an instance of Service from config.

        Args:
            filename (str): Filename of config (default value = "config_vk.ini").
        """
        dirname = os.path.dirname(__file__)
        configfile_path = os.path.join(dirname, filename)

        try:
            config = configparser.ConfigParser()
            config.read(configfile_path, encoding="utf-8")

            user_agent = config["VK"]["user_agent"]
            token = config["VK"]["token_for_audio"]

            return Service(user_agent, token)
        except Exception as e:
            log(f"ERROR in parse_config() -> {e}")

    # GET_AUDIOS_BY_TEXT

    def __get_response_for_search_by_text(
        self, text: str, count: int
    ) -> requests.Response:
        session = requests.session()
        session.headers.update({"User-Agent": self.user_agent})
        response = session.post(
            "https://api.vk.com/method/audio.search",
            data=[
                ("access_token", self.__token),
                ("https", 1),
                ("lang", "ru"),
                ("extended", 1),
                ("v", "5.131"),
                ("q", text),
                ("autocomplete", 1),
                ("sort", 0),
                ("count", count),
            ],
        )
        session.close()
        return response

    @staticmethod
    def __get_musics_from_response(response: requests.Response) -> list[Music]:
        response = json.loads(response.content.decode("utf-8"))
        try:
            items = response["response"]["items"]
        except Exception as e:
            raise Exception(f"ERROR in get_musics_from_response() -> {e}")

        musics: list[Music] = []
        for item in items:
            music = Music.from_json(item)
            musics.append(music)
        return musics

    def get_songs_by_text(self, text: str, count: int = 3) -> list[Music]:
        """
        Search songs by query.

        Args:
            text (str): Text of query. Can be title of song or author, etc.
            count (int): Count of results (default value = 3 songs).

        Returns:
            list[Music]: List of founded songs. Len(list) <= count.
        """
        log(f'Request by text: "{text}" в количестве {count}')
        response = self.__get_response_for_search_by_text(text, count)
        try:
            musics = self.__get_musics_from_response(response)
        except Exception as e:
            log(f"ERROR in get_songs_by_text() / search() -> {e}")
            return

        if len(musics) == 0:
            log("No results found ._.")
        else:
            log("Results:")
            i = 1
            for music in musics:
                print(f"{i}) {music}")
                i += 1
        return musics

    def search(self, text: str, count: int = 3) -> list[Music]:
        """
        Search songs by query. (Same as 'get_songs_by_text()')

        Args:
            text (str): Text of query. Can be title of song or author, etc.
            count (int): Count of results (default value = 3 songs).

        Returns:
            list[Music]: List of founded songs. Len(list) <= count.
        """
        return self.get_songs_by_text(text, count)

    # GET_AUDIOS_BY_USER_ID

    def __get_response_by_userid(
        self, user_id: str or int, count: int, offset: int
    ) -> requests.Response:
        session = requests.session()
        session.headers.update({"User-Agent": self.user_agent})
        response = session.post(
            "https://api.vk.com/method/audio.get",
            data=[
                ("access_token", self.__token),
                ("https", 1),
                ("lang", "ru"),
                ("extended", 1),
                ("v", "5.131"),
                ("owner_id", user_id),
                ("count", count),
                ("offset", offset),
            ],
        )
        session.close()
        return response

    def get_songs_by_userid(
        self, user_id: str or int, count: int = 100, offset: int = 0
    ) -> list[Music]:
        """
        Search songs by id (of user VK).

        Args:
            user_id (str or int): id of user VK. NOT USERNAME! ID after vk.com/id*******
            count (int): Count of results (default value = 100 songs (MAX)).
            offset (int): Set offset of results/ For example, if u need 101-200 -> count = 100, offset = 100.

        Returns:
            list[Music]: List of founded songs. Len(list) <= count.
        """
        user_id = int(user_id)
        print(f"Request by user: {user_id}")
        response = self.__get_response_by_userid(user_id, count, offset)

        try:
            musics = self.__get_musics_from_response(response[0])
        except Exception as e:
            log(f"ERROR in get_songs_by_userid() -> {e}")
            return

        if len(musics) == 0:
            log("No results found ._.")
        else:
            log("Results:")
            i = 1
            for music in musics:
                print(f"{i}) {music}")
                i += 1
        return musics

    # GET_COUNT

    def __get_response_for_count(self, user_id: str or int) -> requests.Response:
        session = requests.session()
        session.headers.update({"User-Agent": self.user_agent})
        response = session.post(
            "https://api.vk.com/method/audio.getCount",
            data=[
                ("access_token", self.__token),
                ("https", 1),
                ("lang", "ru"),
                ("extended", 1),
                ("v", "5.131"),
                ("owner_id", user_id),
            ],
        )
        return response

    def get_count_by_user_id(self, user_id: str or int) -> int:
        """
        Get count of all user's songs.

        Args:
            user_id (str or int): id of user VK. NOT USERNAME! ID after vk.com/id*******

        Returns:
            int: count of all user's songs.
        """
        user_id = int(user_id)
        print(f"Request by user: {user_id}")
        response = self.__get_response_for_count(user_id)
        data = json.loads(response.content.decode("utf-8"))

        try:
            songs_count = int(data["response"])
        except Exception as e:
            log(f"ERROR in get_count_by_user_id() -> {e}")
            return

        log(f"Count of user's songs: {songs_count}")
        return songs_count

    @staticmethod
    def save_music(music: Music) -> str:
        """
        Save song to '{workDirectory}\\Music\\{songname}.mp3'.

        Args:
            music (Music): 'Music' object obtained from methods of the 'Service'.

        Returns:
            str: relative path of downloaded music.
        """
        music = Music.safe(music)
        file_name_mp3 = f"{music}.mp3"
        url = music.url

        if url == "":
            log("Url no found")
            return

        response = requests.get(url=url)
        if response.status_code == 200:
            if not os.path.exists("Music"):
                os.makedirs(f"Music")
                log("Folder 'Music' was created")

            file_path = os.path.join("Music", file_name_mp3)

            if not os.path.exists(file_path):
                if "index.m3u8" in url:
                    log("ERROR in save_music() -> .m3u8 detected!")
                    return
            else:
                log(f"File with name {file_name_mp3} exists. Overwrite it? (Y/n)")

                res = input().lower()
                if res.lower() != "y" and res.lower() != "yes":
                    return

        response.close()
        log(f"Downloading {music}...")
        with open(file_path, "wb") as output_file:
            output_file.write(response.content)

        log(f"Success! Music was downloaded in '{file_path}'")
        return file_path
