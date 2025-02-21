![Лицензия](https://img.shields.io/badge/Лицензия-MIT-blue) ![Совместимость с Python](https://img.shields.io/badge/Python-3.8--3.12-blue) ![Версия библиотеки](https://img.shields.io/badge/pip-3.4.0-blue) [![PyPi downloads](https://img.shields.io/pypi/dm/vkpymusic.svg)](https://pypi.org/project/vkpymusic/) 
<!--- [![PyPi status](https://img.shields.io/pypi/status/vkpymusic.svg?style=flat-square)](https://pypi.python.org/pypi/vkpymusic) --->

# <p align="center"> VKpyMusic 
Click [here](README_EN.md) to switch to **English** version

**VKpyMusic** - это библиотека Python, которая предоставляет простой интерфейс для взаимодействия с API музыкального сервиса **ВКонтакте (VK)**. Библиотека позволяет разработчикам легко выполнять операции, связанные с музыкой и другими функциональными возможностями, доступными через **VK API**. 

# Установка
Библиотека протестирована с Python 3.8-3.12. 
* Установка через pip (менеджер пакетов Python):

	```bash
	$ pip install vkpymusic
	```
* Установка из исходников (требуется `git`):

	```bash
	$ pip install git+https://github.com/issamansur/vkpymusic.git
	```

**Рекомендуется** использование первого варианта.

# Использование

Чтобы начать работу с **VKpyMusic**, вам понадобится действительный токен доступа к **VK** и пользовательский агент, который предоставляет доступ к **API** музыкального сервиса **VK**. Но если у вас их нет, ничего страшного - у нас есть свой собственный класс для их получения.

## <br> Использование класса `TokenReceiver` для получения токена и юзер-агента
Для получения токена **VKpyMusic** задействует класс `TokenReceiver`, который отвечает за выполнение авторизации с использованием доступных логина и пароля. Он предоставляет методы для обработки **captcha**, двухфакторной аутентификации и различных сценариев ошибок. Подробнее о работе класса [здесь](https://issamansur.github.io/vkpymusic/vkpymusic/#vkpymusic.TokenReceiver).

```python
from vkpymusic import TokenReceiver

login = input("   Enter login: ")
password = input("Enter password: ")

tokenReceiver = TokenReceiver(login, password)

if tokenReceiver.auth():
    tokenReceiver.get_token()
    tokenReceiver.save_to_config()
```
### Результат:
```
   Enter login: +...........
Enter password: .........
SMS with a confirmation code has been sent to your phone! The code is valid for a few minutes!
Code: 277765
Token was received!
Token was saved!
```

## <br> Использование класса `Service`
* Для начала работы с аудио вы можете воспользоваться токеном, сгенерированным в прошлом пункте с помощью класса `TokenReceiver`:

	```python
	from vkpymusic import Service
	
	service = Service.parse_config()
	```

* Или указать свой токен и юзер-агент:
	```python
	service = Service("<your_client>", "<your_token>")
	```
Подробнее о работе класса [здесь](https://issamansur.github.io/vkpymusic/vkpymusic/#vkpymusic.Service)
### Получить информацию о песнях текущего пользователя
Следующий код пытается получить 10 треков пользователя. **Обратите внимание, что в качестве первого аргумента принимается только ID пользователя (не username)!** Если аудиозаписи пользователя закрыты, вызывается исключение `VkApiException: VK API Error 201: Access denied`. 
```python
user_songs = service.get_songs_by_userid(123456789, 10)
```

### Поиск треков по запросу
```python
songs = service.search_songs_by_text("Radiohead no surprises", 5)
```

### Получить популярные треки
```python
songs = service.get_popular(count=50, offset=0)
```
### Сохранить трек локально
```python
songs = service.search_songs_by_text("Radiohead no surprises", 5)
Service.save_music(songs[0])
# или
service.save_music(songs[0])
```
## <br> Полный пример
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

# Документация
Детальная документация и примеры использования для **VKpyMusic** находится на официальной странице **GitHub**: 
### https://github.com/issamansur/vkpymusic
### https://issamansur.github.io/vkpymusic/


# Вклад и поддержка
Если у вас есть какие-либо предложения по улучшению **VKpyMusic** или вы обнаружите какие-либо проблемы, пожалуйста, создайте новую проблему на [странице](https://github.com/issamansur/vkpymusic) проекта GitHub. Мы приветствуем ваши запросы на исправления и готовы помочь вам с любыми проблемами, с которыми вы столкнетесь.


## Лицензия
**VKpyMusic** распространяется под лицензией MIT. За более детальной информацией о лицензии обратитесь к файлу LICENSE.

## Авторы
**VKpyMusic** разрабатывается **@issamansur** или/и командой 'EDEXADE, inc.'
