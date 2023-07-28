import subprocess
import os
from bs4 import BeautifulSoup
import requests
import time


def find_mirror(url):
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


def initial_make_directory():
    os.chdir(os.path.expanduser("~"))
    dizin_yolu = os.path.join("data", "ml", "lore.kernel.org")
    os.makedirs(dizin_yolu, exist_ok=True)


def find_git_clone_url(url, link_text):
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


def git_clone(url):
    split_url = url.split("/")
    result = subprocess.run(["git", "clone", url, f"{split_url[-2]}/{split_url[-1]}"])

    if result.returncode == 0:
        output = result.stdout
        print("The cloning process has been completed:", output)
    else:
        error = result.stderr
        print("The cloning process could not be completed.:", error)


def update_git_clone(url):
    split_url = url.split("/")
    result = subprocess.run(["git", "clone", url, f"{split_url[-1]}"])

    if result.returncode == 0:
        output = result.stdout
        print("The update process has been completed:", output)
    else:
        error = result.stderr
        print("The update process could not be completed:", error)


def files_of_directory():
    file_names = os.listdir()

    for file_name in file_names:
        yield file_name


def check_file_existence(file_name):
    return os.path.exists(file_name)


def go_file(file_name):
    try:
        os.chdir(file_name)
        print(f"Entered the file named {file_name}")
    except FileNotFoundError:
        print(f"The file named {file_name} could not be found:")
    except NotADirectoryError:
        print(f"{file_name} is not a directory:")


def exit_file():
    try:
        current_directory = os.getcwd()
        print(f"Exited the directory of {current_directory}")
        os.chdir("..")

    except OSError as e:
        print("Unable to exit the current directory. Error message:\n", e)


def pull_file():
    result = subprocess.run(["git", "pull"])
    if result.returncode == 0:
        print("The file has been updated.")
    else:
        error = result.stderr
        print("The file could not be updated. Error command:", error)


def update_archive(name_archive, link_dict):
    go_file(name_archive)

    b = files_of_directory()
    list_directory = []

    for files_name in b:
        if files_name[0] == ".":
            continue
        list_directory.append(files_name)

    a = find_git_clone_url(link_dict[name_archive], name_archive)
    for git_url in a:
        split_url = git_url.split("/")

        print(list_directory)
        print(split_url[-1])
        if split_url[-1] in list_directory:
            go_file(split_url[-1])
            pull_file()
            exit_file()
        else:
            print(
                f"A new URL({git_url}) was found inside folder {name_archive} and is being downloaded."
            )

            update_git_clone(git_url)
    exit_file()


def git_clone_kernel():
    initial_make_directory()
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
                link_dict[link_text] = find_mirror(url + "/" + link_href)
                print(link_text)

        if "next (older)" in link_dict:
            response = requests.get(link_dict["next (older)"])
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")

        else:
            names_archives_files = []
            for name_file in files_of_directory():
                if name_file[0] == ".":
                    continue
                names_archives_files.append(name_file)

            for name_archive in link_dict.keys():
                if check_file_existence(name_archive):
                    names_archives_files.remove(name_archive)
                    update_archive(name_archive, link_dict)

                else:
                    a = find_git_clone_url(link_dict[name_archive], name_archive)
                    for git_url in a:
                        git_clone(git_url)
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
    git_clone_kernel()
    time.sleep(600)
