
import configparser
import http.client as http_client
import logging
import os
import sys
from urllib.parse import urlencode

import requests

from bs4 import BeautifulSoup

http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def initial_make_directory():
    os.chdir(os.path.expanduser("~"))
    dizin_yolu = os.path.join("data", "ml", "lore.kernel.org")
    os.makedirs(dizin_yolu, exist_ok=True)

def download_file(download_url,file_name):
    response = session.get(download_url)
    if response.status_code == 200:
        with open(file_name, 'wb') as dosya:
            dosya.write(response.content)
        print(f"{file_name} downloaded successfully.")
    else:
        print(f"Error: {response.status_code} - Download failed.")

def list_name_archive_link ():
    url = "https://www.postgresql.org/list"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        if "/list/" in a_tag['href'] and a_tag['href'] != "/list/":
            list_archive_link = list()
            list_archive_link.append(a_tag.get_text())
            list_archive_link.append(url + a_tag['href'][5:])
            yield list_archive_link

def list_date_link(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')

    for row in rows:
        a_tags = row.select('a')
        if a_tags:
            list_date_link = list()
            list_date_link.append(a_tags[0].get_text())
            list_date_link.append(url + a_tags[-1]["href"][18:])
            yield list_date_link
def check_file_existence(file_name):
    return os.path.exists(file_name)

def go_file(file_name):
    if os.path.exists(file_name):
        try:
            os.chdir(file_name)
            print(f"Entered the file named {file_name}")
        except NotADirectoryError:
            print(f"{file_name} is not a directory:")
    else:
        os.makedirs(file_name)
        try:
            os.chdir(file_name)
            print(f"Entered the file named {file_name}")
        except NotADirectoryError:
            print(f"{file_name} is not a directory:")

def exit_file():
    try:
        current_directory = os.getcwd()
        print(f"Exited the directory of {current_directory}")
        os.chdir("..")

    except OSError as e:
        print("Unable to exit the current directory. Error message:\n", e)


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

payload_enc = urlencode(payload)

headers = {
    "Authority": "www.postgresql.org",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Ch-Ua": 'Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "Sec-Ch-Ua-Mobile": '?0',
    "Sec-Ch-Ua-Platform": 'macOS',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Origin": "https://www.postgresql.org",
    "Referer": "https://www.postgresql.org/account/login/?next=/account/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}


import pycurl
csrftoken = session.cookies["csrftoken"]
print(csrftoken)



headers = []
def cb_headers(header_line):
    # HTTP standard specifies that headers are encoded in iso-8859-1.
    header_line = header_line.decode('iso-8859-1')
    if not (':' in header_line):
        return

    # Break the header line into header name and value.
    name, value = header_line.split(':', 1)

    # Remove whitespace that may be present.
    # Header lines include the trailing newline, and there may be whitespace
    # around the colon.
    name = name.strip()
    value = value.strip()

    # Header names are case insensitive.
    # Lowercase name here.
    name = name.lower()

    # Now we can actually record the header name and value.
    # Note: this only works when headers are not duplicated, see below.
    headers.append((name, value))

print("POST PAYLOAD:", payload_enc)
c = pycurl.Curl()
c.setopt(c.URL, "https://www.postgresql.org/account/login/")
c.setopt(c.POSTFIELDS, payload_enc)
c.setopt(c.FOLLOWLOCATION, True)
req_headers = [
#    'authority: www.postgresql.org',
    'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language: tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control: max-age=0',
    'content-type: application/x-www-form-urlencoded',
   f'cookie: csrftoken={csrftoken}',
    'origin: https://www.postgresql.org',
    'referer: https://www.postgresql.org/account/login/?next=/account/',
    'sec-ch-ua: "Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile: ?0',
    'sec-ch-ua-platform: "macOS"',
    'sec-fetch-dest: document',
    'sec-fetch-mode: navigate',
    'sec-fetch-site: same-origin',
    'sec-fetch-user: ?1',
    'upgrade-insecure-requests: 1',
    'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
]
c.setopt(c.HTTPHEADER, req_headers)
c.setopt(c.HEADERFUNCTION, cb_headers)
c.setopt(c.VERBOSE, 1)
c.perform()
c.close()

for k, v in headers:
    print("HHHHHH", k, v)

sys.exit(0)

req2 = session.get("https://www.postgresql.org/account/")
print(req2.cookies)
print(session.cookies)


session.cookies["sessionid"] = "tmzjcyu80f1adi0sdyt3z7i636n09l14"
def download_file2(download_url):
    response = session.get(download_url)
    split_url = download_url.split("/")
    dosya_adi = split_url[-1]
    if response.status_code == 200:
        with open(dosya_adi, 'wb') as dosya:
            dosya.write(response.content)
        print(f"{dosya_adi} downloaded successfully.")
    else:
        print(f"Error: {response.status_code} - Download failed.")


def indir(url, dosya_adi):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(dosya_adi, 'wb') as dosya:
                dosya.write(response.content)
            print(f"{dosya_adi} başarıyla indirildi.")
        else:
            print(f"Hata: {response.status_code} - İndirilemedi.")
    except Exception as e:
        print(f"Hata: {e}")

url = "https://www.postgresql.org/list/pgsql-admin/"  # İndirilecek web sitesinin URL'si
dosya_adi = "psql-admin.html"       # Kaydedilecek dosya adı

#for name_archive_link in list_name_archive_link():
#    go_file(name_archive_link[0])
#    for date_link in list_date_link(name_archive_link[1]):
#        if check_file_existence(date_link[0]): #TODO
#
#            pass
#        else:
#            print(date_link[0],"is being downloaded.")
#            download_file(date_link[1],date_link[0])
#    exit_file()
#
#
