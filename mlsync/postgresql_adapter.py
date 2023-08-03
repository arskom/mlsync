import configparser
import os
import requests
from bs4 import BeautifulSoup
import time
import datetime


def initial_make_directory():
    os.chdir(os.path.expanduser("~"))
    dizin_yolu = os.path.join("data", "ml", "postgresql.org")
    os.makedirs(dizin_yolu, exist_ok=True)


def download_file(download_url, file_name):
    response = session.get(download_url)
    if response.status_code == 200:
        with open(file_name + ".tmp", "wb") as dosya:
            dosya.write(response.content)
        print(f"{file_name} downloaded successfully.")
        os.rename(file_name + ".tmp", file_name)
        return os.path.getsize(file_name)
    else:
        print(
            f"{file_name} could not be downloaded.",
            f"Error: {response.status_code} - Download failed.",
        )


def list_name_archive_link():
    url = "https://www.postgresql.org/list"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    a_tags = soup.find_all("a")
    for a_tag in a_tags:
        if "/list/" in a_tag["href"] and a_tag["href"] != "/list/":
            list_archive_link = list()
            if "/" in a_tag.get_text():
                list_archive_link.append(a_tag.get_text().replace("/", "-"))  # TODO
            else:
                list_archive_link.append(a_tag.get_text())
            list_archive_link.append(url + a_tag["href"][5:])
            yield list_archive_link


def list_date_link(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr")

    for row in rows:
        a_tags = row.select("a")
        if a_tags:
            list_date_link = list()
            split_name = a_tags[0].get_text().split(" ")
            split_href = a_tags[-1]["href"].split("/")

            list_date_link.append(split_name[-1] + "-" + split_name[0])
            list_date_link.append(url + split_href[-2] + "/" + split_href[-1])
            yield list_date_link


def check_directory_existence(file_name):
    return os.path.exists(file_name)


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


def exit_directory():
    try:
        current_directory = os.getcwd()
        print(f"Exited the directory of {current_directory}")
        os.chdir("..")

    except OSError as e:
        print("Unable to exit the current directory. Error message:\n", e)


def log_in():
    global session
    config = configparser.ConfigParser()
    config.read("/Users/burak/src/mlsync/mlsync/config.ini")

    username = config.get("Credentials", "username")
    password = config.get("Credentials", "password")

    session = requests.Session()
    response = session.get("https://www.postgresql.org/account/login/")

    soup = BeautifulSoup(response.text, "html.parser")
    csrfmiddlewaretoken = soup.find("input", {"name": "csrfmiddlewaretoken"}).get(
        "value"
    )
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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    url = "https://www.postgresql.org/account/login/"

    session.post(url, data=payload, headers=headers)
    print(session.cookies)


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


def current_and_previous_month():
    current_date = datetime.datetime.now()
    previous_month = current_date - datetime.timedelta(days=current_date.day)  # TODO

    current_date_str = current_date.strftime("%Y-%m")
    previous_month_str = previous_month.strftime("%Y-%m")
    return current_date_str, previous_month_str


def postgresql_download_update():
    log_in()
    a = 0
    for name_archive_link in list_name_archive_link():
        print(name_archive_link)
        ensure_directory(name_archive_link[0])
        update_list = []
        delete_tmp()
        for date_link in list_date_link(name_archive_link[1]):

            print(date_link)
            months = {
                "January": "01",
                "February": "02",
                "March": "03",
                "April": "04",
                "May": "05",
                "June": "06",
                "July": "07",
                "August": "08",
                "September": "09",
                "October": "10",
                "November": "11",
                "December": "12",
            }
            if check_directory_existence(date_link[0]):
                split_file_name = date_link[0].split("-")
                to_compare_file_name = (
                    split_file_name[0] + "-" + months[f"{split_file_name[1]}"]
                )

                current_date_str, previous_month_str = current_and_previous_month()

                if (
                    to_compare_file_name == current_date_str
                    or to_compare_file_name == previous_month_str
                ):
                    update_list.append(date_link)

            else:
                print(date_link[0], "is being downloaded.")
                try:
                    a += download_file(date_link[1], date_link[0])
                except Exception as excep:
                    print("Error message:", excep)
                    print("Resuming operations in 10 seconds...")
                    time.sleep(10)
                    print("Continuing operations now...")
                    log_in()
                    print("Bytes downloaded until the server does not respond:", a)
                    a = 0
                    a += download_file(date_link[1], date_link[0])
                print(a)

        for date_link in update_list:
            print(date_link[0], "is being updated...")
            try:
                a += download_file(date_link[1], date_link[0])
            except Exception as excep:
                print("Error message:", excep)
                print("Resuming operations in 10 seconds...")
                time.sleep(10)
                print("Continuing operations now...")
                log_in()
                print("Bytes downloaded until the server does not respond:", a)
                a = 0
                a += download_file(date_link[1], date_link[0])
            print(a)

        exit_directory()


postgresql_download_update()
