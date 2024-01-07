from vkpymusic import Service

service = Service.parse_config()

# or you can do like this
# service = Service("<your_user_agent>", "<your_token>")

if service is not None:
    if not service.is_token_valid():
        print("Token expired!")
        print("Run first 'receive_token_example.py'")
        exit()
    songs = service.search_songs_by_text(input())
    if songs:
        service.save_music(songs[0])
    else:
        print("No songs found ._.")
else:
    print("File config not found!")
    print("Run first 'receive_token_example.py'")
