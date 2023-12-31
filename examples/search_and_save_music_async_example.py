from vkpymusic import ServiceAsync

import asyncio


async def main():
    service = ServiceAsync.parse_config()
    # or you can do like this
    # service = Service("<your_user_agent>", "<your_token>")

    if service is not None:
        if not await service.check_token():
            print("Token expired!")
            print("Run first 'receive_token_example.py'")
            return

        songs = await service.search_songs_by_text(input())
        if songs:
            await service.save_music(songs[0])
        else:
            print("No songs found ._.")
    else:
        print("File config not found!")
        print("Run first 'receive_token_example.py'")


asyncio.run(main())
