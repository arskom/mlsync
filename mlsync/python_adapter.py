import requests
from bs4 import BeautifulSoup
import os
import subprocess
import datetime
from dateutil.relativedelta import relativedelta


def find_archive_link(url):
    response = requests.get(url)

    if response.status_code != 200:
        print(url, "is not accessible.")

    soup = BeautifulSoup(response.content, "html.parser")

    for link in soup.find_all("a"):
        href = link.get("href")
        text = link.text.strip()
        if text == "This month (mbox)":
            b = url.split("/")
            url = "/".join(b[:3])
            return url + href


def ensure_directory(file_name):
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

    result = subprocess.run(["curl", "-o", f"{url[-25:-18]}.mbox.gz.tmp", "-L", url])

    if result.returncode == 0:
        print(f"{url[-25:-18]}.mbox.gz downloaded successfully.")
        os.rename(f"{url[-25:-18]}.mbox.gz.tmp", f"{url[-25:-18]}.mbox.gz")

    else:
        error = result.stderr
        print("The cloning process could not be completed.:", error)


def go_to_next_month_url(url):
    end_date = url[-10:]
    start_date = url[-25:-15]
    archive_name = url[-25:-18]
    date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    previous_month = relativedelta(months=1)
    new_date = date_obj + previous_month
    new_date_str = new_date.strftime("%Y-%m-%d")
    url = url.replace(end_date, new_date_str)
    url = url.replace(start_date, end_date)
    url = url.replace(archive_name, end_date[:-3], 1)
    return url


def previous_and_current_and_next_month():
    current_date = datetime.datetime.now()
    previous_month = current_date - datetime.timedelta(days=current_date.day)
    next_month = current_date.replace(day=28) + datetime.timedelta(days=4)
    if next_month.month != current_date.month:
        next_month = next_month.replace(day=1)

    current_date_str = current_date.strftime("%Y-%m")
    previous_month_str = previous_month.strftime("%Y-%m")
    next_month_str = next_month.strftime("%Y-%m")
    return previous_month_str, current_date_str, next_month_str
def delete_tmp():
    for find_td in os.listdir():
        if find_td[0] == ".":
            continue
        elif find_td[-4:] == ".tmp":
            os.remove(find_td)
            print(
                f"{find_td} was found and deleted. {find_td[:-4]} will be downloaded later in the code."
            )
            time.sleep(5)

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
        previous, current, future = previous_and_current_and_next_month()
        for i in dict_archive_links:
            ensure_directory(i)
            link_archive = find_archive_link(dict_archive_links[i])

            end_date = link_archive[-10:]
            start_date = link_archive[-25:-15]
            archive_name = link_archive[-25:-18]

            new_end_date = "1970-02-01"
            new_start_date = "1970-01-01"
            new_archive_name = "1970-01"

            link_archive = link_archive.replace(start_date, new_start_date)
            link_archive = link_archive.replace(end_date, new_end_date)
            link_archive = link_archive.replace(archive_name, new_archive_name, 1)
            delete_tmp()
            while link_archive[-25:-18] != current:  # FIXME
                if os.path.exists(f"{link_archive[-10:]}.mbox.gz"):
                    download_file(url)
                    go_to_next_month_url(url)
                    download_file(url)
                    print("The update for python is complete.")

                    print("Update was completede")
                elif os.path.exists(f"{link_archive[-25:-18]}.mbox.gz"):
                    print(link_archive[-25:-18],"already exists.")
                    link_archive = go_to_next_month_url(link_archive)
                else:
                    download_file(link_archive)
                    link_archive = go_to_next_month_url(link_archive)

            exit_file()
        break
