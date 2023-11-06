from vkpymusic import ServiceAsync

import asyncio


async def main():
    service = ServiceAsync.parse_config()
    # or you can do like this
    # service = Service("<your_token>", "<your_client>")

    if service is not None:
        songs = await service.search_songs_by_text(input())
        if len(songs) != 0:
            await service.save_music(songs[0])
    else:
        print("File config not found!")
        print("Run first 'examples\\receive_token_example.py'")


asyncio.run(main())
