from vktoken import TokenReceiver

login = input('   Enter login: ')
password = input('Enter password: ')

tr: TokenReceiver = TokenReceiver(login, password)

if tr.auth():
    tr.get_token()
    tr.save_to_config()
