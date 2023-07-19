import subprocess
import os
from bs4 import BeautifulSoup
import requests


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


def find_git_clone_code(url, link_text):
    # Web sayfasını indirin
    response = requests.get(url)

    # İçeriği analiz etmek için BeautifulSoup kullanın
    soup = BeautifulSoup(response.content, "html.parser")

    # Verilen anahtar kelimeye sahip olan linkleri seçin ve döndürün
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
    result = subprocess.run(
        ["git " + "clone " + url + f" {split_url[-2]}/{split_url[-1]}"], shell=True,
    )  # TODO komutun inputu link olacak ve target belirle !!!

    if result.returncode == 0:
        output = result.stdout
        print("Komut çıktısı:\n", output)
    else:
        error = result.stderr
        print("Hata mesajı:\n", error)


def files_of_kernel():
    dizin = "/kernel"  # Dizin yolunu buraya girin
    dosya_adlari = os.listdir(dizin)

    for dosya_adi in dosya_adlari:
        yield dosya_adi


def force_find_files_git_code(key_word):
    url = "https://lore.kernel.org"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = soup.find_all("a")
    href_next = ""
    while True:
        for link in links:
            link_text = link.text.strip()
            link_href = link.get("href")
            if link_text == key_word:
                return find_git_clone_code(find_mirror(url + "/" + link_href), key_word)
            elif link_text == "next (older)":
                href_next = link_href
                url = "https://lore.kernel.org/" + href_next
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")

                links = soup.find_all("a")


def check_file_existence(file_name):
    return os.path.exists(file_name)


def go_file(file_name):

    result = subprocess.run(["cd " + "/" + file_name], shell=True,)
    if result.returncode == 0:
        output = result.stdout
        print(f"{file_name} adlı dosyaya girdi.")
    else:
        error = result.stderr
        print(f"{file_name} adlı dosyaya giremedi.Hata komutu:\n", error)


def exit_file():
    result = subprocess.run(["cd " + ".."], shell=True,)
    if result.returncode == 0:
        output = result.stdout
        print("Dosyadan çıkış yapıldı.")
    else:
        error = result.stderr
        print("Dosyadan çıkılırken hata oldu. Hata komutu:\n", error)


def pull_file():
    result = subprocess.run(["git " + "pull"], shell=True,)
    if result.returncode == 0:
        output = result.stdout
        print("Dosyadan çıkış yapıldı.")
    else:
        error = result.stderr
        print("Dosyadan çıkılırken hata oldu. Hata komutu:\n", error)


def git_clone_kernel(url):  # url = "https://lore.kernel.org" #Bitmediiiiii !!!!
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = soup.find_all("a")
    link_dict = {}
    while True:
        for link in links:
            link_text = link.text.strip()
            link_href = link.get("href")

            if (
                link_text != "all"
            ):  # if type(find_mirror(url + "/" + link_href)) == str and link_text != "all":
                if link_text != "next (older)" and link_text != "reverse":
                    link_dict[link_text] = find_mirror(url + "/" + link_href)
                    print(link_text)
                elif link_text == "next (older)":
                    link_dict[link_text] = url + "/" + link_href
                    print(link_text)

        if "next (older)" in link_dict:
            response = requests.get(link_dict["next (older)"])
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")

        if not "next (older)" in link_dict:
            a = files_of_kernel()
            for i in a:
                pass

            for i in link_dict.keys():
                if check_file_existence(i):
                    print(i, "dosyası zaten bulunmaktadır")
                else:
                    print(link_dict[i], "dosyası indiriliyor...")
                    a = find_git_clone_code(link_dict[i], i)
                    for git_code in a:
                        git_clone(git_code)
            print("kod çıktı ")  # TODO sil buraları
            break

        del link_dict["next (older)"]
