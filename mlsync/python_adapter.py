import requests
from bs4 import BeautifulSoup
import os
import subprocess


def find_archive_link(url):
    response = requests.get(url)

    if response.status_code != 200:
        print("Siteye erişilemedi.")
        exit()

    soup = BeautifulSoup(response.content, "html.parser")

    data = {}

    for link in soup.find_all("a"):
        href = link.get("href")
        text = link.text.strip()
        if text == "Entire archive (mbox)":
            b = url.split("/")
            url = "/".join(b[:3])
            data[text] = url + href
            return data[text]


def go_file(file_name):
    try:
        os.chdir(file_name)
        print(f"Entered the file named {file_name}")
    except FileNotFoundError:
        print(f"The file named {file_name} could not be found:")
    except NotADirectoryError:
        print(f"{file_name} is not a directory:")


def make_directory(name_directory):
    import os

    directory_path = name_directory

    try:
        os.mkdir(directory_path)
        print(f"{directory_path} dizini oluşturuldu.")
    except FileExistsError:
        print(f"{directory_path} dizini zaten mevcut.")


def exit_file():
    try:
        current_directory = os.getcwd()
        print(f"Exited the directory of {current_directory}")
        os.chdir("..")

    except OSError as e:
        print("Unable to exit the current directory. Error message:\n", e)


def download_file(url):
    split_url = url.split("/")
    result = subprocess.run(["curl -o  " + split_url[-1] + " -L " + url], shell=True,)

    if result.returncode == 0:
        output = result.stdout
        print("The cloning process has been completed:", output)
    else:
        error = result.stderr
        print("The cloning process could not be completed.:", error)


url = "https://mail.python.org/archives/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
dict_archive_links = {}
links = soup.find_all("a")
while True:
    for link in links:
        href = link.get("href")
        text = link.text.strip()
        if text == "":
            continue
        elif "/archives/list/" in href:
            dict_archive_links[text] = url + href[10:]
            print(text, dict_archive_links[text])
        elif text == "Next →":
            dict_archive_links[text] = url + href
            print(text, dict_archive_links[text])

    if "Next →" in dict_archive_links and "page" in dict_archive_links["Next →"]:
        response = requests.get(dict_archive_links["Next →"])
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a")
        del dict_archive_links["Next →"]
    else:
        del dict_archive_links["Next →"]
        for i in dict_archive_links:
            make_directory(i)
            go_file(i)
            a = find_archive_link(dict_archive_links[i])
            download_file(a)
            exit_file()
        break
