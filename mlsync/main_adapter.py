import subprocess
import os
from bs4 import BeautifulSoup
import time
import requests
import datetime
from dateutil.relativedelta import relativedelta
import configparser

# Common functions
def initial_make_directory(directory_name):
    os.chdir(os.path.expanduser("~"))
    path = os.path.join("data", "ml", directory_name)
    os.makedirs(path, exist_ok=True)
    os.chdir(path)


def find_archive_link_python(url):
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


def exit_directory():
    try:
        current_directory = os.getcwd()
        print(f"Exited the directory of {current_directory}")
        os.chdir("..")

    except OSError as e:
        print("Unable to exit the current directory. Error message:\n", e)


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


# Python's functions


def download_file_python(url):

    result = subprocess.run(["curl", "-o", f"{url[-25:-18]}.mbox.gz.tmp", "-L", url])

    if result.returncode == 0:
        print(f"{url[-25:-18]}.mbox.gz downloaded successfully.")
        os.rename(f"{url[-25:-18]}.mbox.gz.tmp", f"{url[-25:-18]}.mbox.gz")

    else:
        error = result.stderr
        print("The cloning process could not be completed.:", error)


def python_download_update():
    initial_make_directory("mail.python.org")
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
                link_archive = find_archive_link_python(dict_archive_links[i])

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
                while link_archive[-25:-18] != future:

                    if (
                        link_archive[-25:-18] == previous
                        or link_archive[-25:-18] == current
                    ):
                        download_file_python(link_archive)
                        link_archive = go_to_next_month_url(link_archive)

                    elif os.path.exists(f"{link_archive[-25:-18]}.mbox.gz"):
                        print(link_archive[-25:-18], "already exists.")
                        link_archive = go_to_next_month_url(link_archive)
                    else:
                        download_file_python(link_archive)
                        link_archive = go_to_next_month_url(link_archive)

                exit_directory()
            break


# Kernel's functions


def download_file_kernel(url):
    split_url = url.split("/")
    result = subprocess.run(["git", "clone", url, f"{split_url[-2]}/{split_url[-1]}"])

    if result.returncode == 0:
        output = result.stdout
        print("The cloning process has been completed:", output)
    else:
        error = result.stderr
        print("The cloning process could not be completed.:", error)


def find_mirror_kernel(url):
    target_text = "mirror"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        link = soup.find("a", string=target_text)
        if link:
            link_url = link.get("href")
            return url + "/" + link_url
        else:
            print("Failed to reach the mirror link.")
    else:
        print("Page could not be fetched. Error code:", response.status_code)


def find_git_clone_url_kernel(url, link_text):
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")

    for link in soup.find_all("a"):
        link_split = link.text.split("/")
        if (
            link_text in link.text
            and len(link_split) == 5
            and link_split[0:3] == ["http:", "", "lore.kernel.org"]
            and link_split[-2] == link_text
            and link_split[-1].isdigit()
        ):
            yield link.get("href")


def update_git_clone_kernel(url):
    split_url = url.split("/")
    result = subprocess.run(["git", "clone", url, f"{split_url[-1]}"])

    if result.returncode == 0:
        output = result.stdout
        print("The update process has been completed:", output)
    else:
        error = result.stderr
        print("The update process could not be completed:", error)


def pull_file_kernel():
    result = subprocess.run(["git", "pull"])
    if result.returncode == 0:
        print("The file has been updated.")
    else:
        error = result.stderr
        print("The file could not be updated. Error command:", error)


def update_archive_kernel(name_archive, link_dict):
    ensure_directory(name_archive)

    b = os.listdir()
    list_directory = []

    for files_name in b:
        if files_name[0] == ".":
            continue
        list_directory.append(files_name)

    a = find_git_clone_url_kernel(link_dict[name_archive], name_archive)
    for git_url in a:
        split_url = git_url.split("/")

        print(list_directory)
        print(split_url[-1])
        if split_url[-1] in list_directory:
            ensure_directory(split_url[-1])
            pull_file_kernel()
            exit_directory()
        else:
            print(
                f"A new URL({git_url}) was found inside folder {name_archive} and is being downloaded."
            )

            update_git_clone_kernel(git_url)
    exit_directory()


def kernel_download_update():
    initial_make_directory("mail.python.org")
    url = "https://lore.kernel.org"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = soup.find_all("a")
    link_dict = {}
    while True:
        for link in links:
            link_text = link.text.strip()
            link_href = link.get("href")

            if link_text == "all":
                continue

            if link_text == "reverse":
                continue

            if link_text == "next (older)":
                link_dict[link_text] = url + "/" + link_href

            else:
                link_dict[link_text] = find_mirror_kernel(url + "/" + link_href)
                print(link_text)

        if "next (older)" in link_dict:
            response = requests.get(link_dict["next (older)"])
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")

        else:
            names_archives_files = []
            file_names = os.listdir()
            for name_file in file_names:
                if name_file[0] == ".":
                    continue
                names_archives_files.append(name_file)

            for name_archive in link_dict.keys():
                if os.path.exists(name_archive):
                    names_archives_files.remove(name_archive)
                    update_archive_kernel(name_archive, link_dict)

                else:
                    a = find_git_clone_url_kernel(link_dict[name_archive], name_archive)
                    for git_url in a:
                        download_file_kernel(git_url)
            if len(names_archives_files) != 0:
                for files_name in names_archives_files:
                    print(
                        f"Just to inform you, the file named **** {files_name} **** was not updated."
                    )
            else:
                print(
                    "*****The update has been successfully performed for all files.*****"
                )

            print("The download and update stages in the kernel are complete.")
            break

        del link_dict["next (older)"]


# Postgresql's functions
def download_file_psql(download_url, file_name):
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


def find_name_archive_and_link_psql():
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


def find_date_and_link_psql(url):
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


def log_in_psql():
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


def postgresql_download_update():
    initial_make_directory("postgresql.org")
    log_in_psql()
    a = 0
    for name_archive_link in find_name_archive_and_link_psql():
        print(name_archive_link)
        ensure_directory(name_archive_link[0])
        delete_tmp()
        for date_link in find_date_and_link_psql(name_archive_link[1]):

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
            if os.path.exists(date_link[0]):
                split_file_name = date_link[0].split("-")
                to_compare_file_name = (
                    split_file_name[0] + "-" + months[f"{split_file_name[1]}"]
                )

                (
                    previous_month_str,
                    current_date_str,
                    next_month_str,
                ) = previous_and_current_and_next_month()

                if (
                    to_compare_file_name == current_date_str
                    or to_compare_file_name == previous_month_str
                ):
                    print(date_link[0], "is being updated...")
                    try:
                        a += download_file_psql(date_link[1], date_link[0])
                    except Exception as excep:
                        print("Error message:", excep)
                        print("Resuming operations in 10 seconds...")
                        time.sleep(10)
                        print("Continuing operations now...")
                        log_in_psql()
                        print("Bytes downloaded until the server does not respond:", a)
                        a = 0
                        a += download_file_psql(date_link[1], date_link[0])
                    print(a)

            else:
                print(date_link[0], "is being downloaded.")
                try:
                    a += download_file_psql(date_link[1], date_link[0])
                except Exception as excep:
                    print("Error message:", excep)
                    print("Resuming operations in 10 seconds...")
                    time.sleep(10)
                    print("Continuing operations now...")
                    log_in_psql()
                    print("Bytes downloaded until the server does not respond:", a)
                    a = 0
                    a += download_file_psql(date_link[1], date_link[0])
                print(a)

        exit_directory()


while True:
    start_time = time.time()

    python_download_update()
    postgresql_download_update()
    kernel_download_update()

    end_time = time.time()
    passing_time = end_time - start_time

    if passing_time > 600:
        continue
    time.sleep(600 - passing_time)
