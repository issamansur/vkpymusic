from vkpymusic.MusicService import Service

service = Service.parse_config()

# or you can do like this
# service = Service("<your_token>", "<your_client>")

if service is not None:
    musics = service.get_songs_by_text("idfc blackbear remix tik tok")
    number = int(input("What music need to download (or any for cancel): "))
    if number >= 0 and number <= len(musics):
        service.save_music(musics[number - 1])
else:
    print("File config not found!")
    print("Run first 'examples\\receive_token_example.py'")
