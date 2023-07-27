from bs4 import BeautifulSoup
import requests
import configparser

def download_file(download_url,file_name):
    response = session.get(download_url)
    if response.status_code == 200:
        with open(file_name, 'wb') as dosya:
            dosya.write(response.content)
        print(f"{file_name} downloaded successfully.")
    else:
        print(f"Error: {response.status_code} - Download failed.")

def dict_name_archive_link ():
    url = "https://www.postgresql.org/list"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    a_tags = soup.find_all('a')
    dict_archive_link = {}
    for a_tag in a_tags:
        if "/list/" in a_tag['href'] and a_tag['href'] != "/list/":
            dict_archive_link[a_tag.get_text()] = url + a_tag['href'][5:]
    return dict_archive_link

def dict_date_link(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')
    dict_date_link = {}

    for row in rows:
        a_tags = row.select('a')
        if a_tags:
            dict_date_link[a_tags[0].get_text()] = url + a_tags[-1]["href"][18:]
    return dict_date_link

config = configparser.ConfigParser()
config.read('config.ini')

username = config.get('Credentials', 'username')
password = config.get('Credentials', 'password')

session = requests.Session()
response = session.get("https://www.postgresql.org/account/login/")
soup = BeautifulSoup(response.text, "html.parser")
csrfmiddlewaretoken = soup.find("input", {"name": "csrfmiddlewaretoken"}).get("value")
this_is_the_login_form = soup.find("input", {"name": "this_is_the_login_form"}).get(
    "value"
)
next_input = soup.find("input", {"name": "next"}).get("value")
payload = {
    "csrfmiddlewaretoken": csrfmiddlewaretoken,
    "this_is_the_login_form": this_is_the_login_form,
    "username": username,
    "password": password,
}

headers = {
    "Origin": "https://www.postgresql.org",
    "Referer": "https://www.postgresql.org/account/login/?next=/account/",
}

post = session.post(
    "https://www.postgresql.org/account/login/", data=payload, headers=headers
)


