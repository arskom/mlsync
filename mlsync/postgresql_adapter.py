from bs4 import BeautifulSoup
import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

username = config.get('Credentials', 'username')
password = config.get('Credentials', 'password')


session = requests.Session()
response = session.get("https://www.postgresql.org/account/login/")
soup = BeautifulSoup(response.text, 'html.parser')
csrfmiddlewaretoken = soup.find('input', {'name': 'csrfmiddlewaretoken'}).get('value')
this_is_the_login_form = soup.find('input', {'name': 'this_is_the_login_form'}).get('value')
next_input = soup.find('input', {'name': 'next'}).get('value')
print(csrfmiddlewaretoken)
payload = {
    "csrfmiddlewaretoken": csrfmiddlewaretoken,
    "this_is_the_login_form": this_is_the_login_form,
    "username": username,
    "password": password
}

headers = {
    "Origin":'https://www.postgresql.org',
    'Referer': 'https://www.postgresql.org/account/login/?next=/account/'
}

post = session.post("https://www.postgresql.org/account/login/", data=payload,headers=headers)
print(post.status_code)



