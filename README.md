![Лицензия](https://img.shields.io/badge/Лицензия-MIT-blue)
![Совместимость с Python](https://img.shields.io/badge/Python-3.7--3.9-blue)
![Версия библиотеки](https://img.shields.io/badge/pip-3.3.0-blue)

# VKpyMusic 
### is a Python library that provides a simple interface for interacting with the VKontakte (VK) music service API. The library allows developers to easily perform operations related to music and other functionalities available through the VK API.
### это библиотека Python, которая предоставляет простой интерфейс для взаимодействия с API музыкального сервиса ВКонтакте (VK). Библиотека позволяет разработчикам легко выполнять операции, связанные с музыкой и другими функциональными возможностями, доступными через VK API.

# Installation
### You can install VKpyMusic using the pip package manager. Open your command prompt or terminal and execute the following command:
### Вы можете установить VKpyMusic с помощью менеджера пакетов pip. Откройте командную строку или терминал и выполните следующую команду:

### Console:
```
pip install vkpymusic
```

# Usage
### To get started with VKpyMusic, you will need a valid VK access token and user agent, which provides access to the VK music service API. But if you don't have them, it's okay - we have our own class to get it.
### Чтобы начать работу с VKpyMusic, вам понадобится действительный токен доступа к VK и пользовательский агент, который предоставляет доступ к API музыкального сервиса VK. Но если у вас их нет, ничего страшного - у нас есть свой собственный класс, чтобы получить их.

## Example usage of VKpyMusic for receive token and user agent:<br>Пример использования VKpyMusic для получения токена и юзер-агента:
### Python:
```
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
## Create an Service instance with your access token and user agent:<br>Создайте экземпляр Service с вашим токеном и юзер-агентом:
### Python:
```
from vkpymusic import Service

service = Service.parse_config()
```
## Or you can do like this:<br>Или Вы можете сделать так:
### Python:
```
service = Service("<your_token>", "<your_client>")
```

## Get information about the current user<br>Получить информацию о песнях текущего пользователя
### Python:
```
user_songs = service.get_songs_by_userid(5, 10)
```

## Search for tracks by query<br>Поиск треков по запросу
### Python:
```
songs = service.search_songs_by_text("Maroon V", 5)
```

## Full example<br>Полный пример
### Python:
```
from vkpymusic import Service, TokenReceiver
login = input("   Enter login: ")
password = input("Enter password: ")

tokenReceiver = TokenReceiver(login, password)

if tokenReceiver.auth():
    tokenReceiver.get_token()
    tokenReceiver.save_to_config()

service = Service.parse_config()
tracks = service.search_songs_by_text('idfc tiktok remix')
Service.save_music(tracks[0])
```

# Documentation<br>Документация
### Detailed documentation and usage examples for VKpyMusic can be found on the official project page on GitHub: 
### Детальная документация и примеры использования для VKpyMusic находится на официальной странице на ГитХабе: 
## https://github.com/issamansur/vkpymusic
## https://issamansur.github.io/vkpymusic/


# Contributions and Support
### Если у вас есть какие-либо предложения по улучшению VKpyMusic или вы обнаружите какие-либо проблемы, пожалуйста, создайте новую проблему на странице проекта GitHub. Мы приветствуем ваши запросы на исправления и готовы помочь вам с любыми проблемами, с которыми вы столкнетесь.
### If you have any suggestions for improving VKpyMusic or if you find any issues, please create a new issue on the GitHub project page. We welcome your pull requests and are here to assist you with any problems you encounter.

# License
### VKpyMusic is distributed under the MIT license. For detailed information about the license, see the LICENSE file.

# Authors
### VKpyMusic is developed by the @issamansur or/and 'EDEXADE, inc.' development team.
