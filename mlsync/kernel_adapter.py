import subprocess
import os
from bs4 import BeautifulSoup
import requests
import time


def initial_make_directory():
    os.chdir(os.path.expanduser("~"))
    dizin_yolu = os.path.join("data", "ml", "mail.python.org")
    os.makedirs(dizin_yolu, exist_ok=True)
    os.chdir(dizin_yolu)


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


def download_file_kernel(url):
    split_url = url.split("/")
    result = subprocess.run(["git", "clone", url, f"{split_url[-2]}/{split_url[-1]}"])

    if result.returncode == 0:
        output = result.stdout
        print("The cloning process has been completed:", output)
    else:
        error = result.stderr
        print("The cloning process could not be completed.:", error)


def update_git_clone_kernel(url):
    split_url = url.split("/")
    result = subprocess.run(["git", "clone", url, f"{split_url[-1]}"])

    if result.returncode == 0:
        output = result.stdout
        print("The update process has been completed:", output)
    else:
        error = result.stderr
        print("The update process could not be completed:", error)


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
    # initial_make_directory()
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


while True:
    kernel_download_update()
    time.sleep(600)
