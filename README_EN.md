![Лицензия](https://img.shields.io/badge/Лицензия-MIT-blue) ![Совместимость с Python](https://img.shields.io/badge/Python-3.8--3.12-blue) ![Версия библиотеки](https://img.shields.io/badge/pip-3.4.1-blue) [![PyPi downloads](https://img.shields.io/pypi/dm/vkpymusic.svg)](https://pypi.org/project/vkpymusic/) 
<!--- [![PyPi status](https://img.shields.io/pypi/status/vkpymusic.svg?style=flat-square)](https://pypi.python.org/pypi/vkpymusic) --->

# <p align="center"> VKpyMusic 
Нажмите [здесь](README_RU.md) для перехода на **русскую** версию

**VKpyMusic** is a Python library that provides a simple interface for interacting with the **VKontakte (VK)** music service API. The library allows developers to easily perform operations related to music and other functionality available through the **VK API**.

# Installation
This library is tested with Python 3.8-3.12.
* Installation using pip (a Python package manager):

	```bash
	$ pip install vkpymusic
	```
* Installation from source (requires `git`):

	```bash
	$ pip install git+https://github.com/issamansur/vkpymusic.git
	```

It is generally **recommended** to use the first option.

# Usage

To get started with **VKpyMusic**, you will need a valid **VK access token** and user agent, which provides access to the **VK music service API**. But if you don't have them, it's okay - we have our own class to obtain it.

## <br> Using `TokenReceiver` class to retrieve token and user agent
To obtain a token, **VKpyMusic** uses the `TokenReceiver` class, which is responsible for performing authorization using the available login and password. It provides methods to handle **captcha**, two-factor authentication, and various error scenarios. Learn more about how the class works [here](https://issamansur.github.io/vkpymusic/vkpymusic/#vkpymusic.TokenReceiver).

```python
from vkpymusic import TokenReceiver

login = input("   Enter login: ")
password = input("Enter password: ")

tokenReceiver = TokenReceiver(login, password)

if tokenReceiver.auth():
    tokenReceiver.get_token()
    tokenReceiver.save_to_config()
```
### Result:
```
   Enter login: +...........
Enter password: .........
SMS with a confirmation code has been sent to your phone! The code is valid for a few minutes!
Code: 277765
Token was received!
Token was saved!
```

## <br> Using the `Service` class
* To get started with audio, you can use the token generated in the previous paragraph using the class `TokenReceiver`:

	```python
	from vkpymusic import Service
	
	service = Service.parse_config()
	```

* Or specify your token and user agent:
	```python
	service = Service("<your_client>", "<your_token>")
	```
Learn more about how the class works [here](https://issamansur.github.io/vkpymusic/vkpymusic/#vkpymusic.Service)

### Get information about the songs of the current user
The following code attempts to retrieve 10 tracks of user. **Note that only the user ID (not username) is acceptable as the first argument!** If the user's audios are closed, an exception `VkApiException: VK API Error 201: Access denied` is thrown. 
```python
user_songs = service.get_songs_by_userid(123456789, 10)
```

### Search for tracks by query
```python
songs = service.search_songs_by_text("Radiohead no surprises", 5)
```

### Get popular tracks
```python
songs = service.get_popular(count=50, offset=0)
```
### Save track locally
```python
songs = service.search_songs_by_text("Radiohead no surprises", 5)
Service.save_music(songs[0])
# or
service.save_music(songs[0])
```
## <br> Full example
```python
from vkpymusic import Service, TokenReceiver

login = input("   Enter login: ")
password = input("Enter password: ")

tokenReceiver = TokenReceiver(login, password)

if tokenReceiver.auth():
    tokenReceiver.get_token()
    tokenReceiver.save_to_config()

service = Service.parse_config()
tracks = service.search_songs_by_text('Radiohead no surprises')
Service.save_music(tracks[0])
```

# Documentation
Detailed documentation and use cases for **VKpyMusic** can be found on the official **GitHub** page: 
### https://github.com/issamansur/vkpymusic
### https://issamansur.github.io/vkpymusic/


# Contributions and Support
If you have any suggestions for improving **VKpyMusic** or if you find any issues, please create a new issue on the GitHub project [page](https://github.com/issamansur/vkpymusic) We welcome your pull requests and are here to assist you with any problems you encounter.
## License
**VKpyMusic** is distributed under the MIT license. For detailed information about the license, see the LICENSE file.

## Authors
**VKpyMusic** is developed by the **@issamansur** or/and 'EDEXADE, inc.' development team.
