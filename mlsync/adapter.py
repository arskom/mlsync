import subprocess

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
            return link_url
        else:
            print("Hedef metin için bağlantı bulunamadı.")
    else:
        print("Sayfa çekilemedi. Hata kodu:", response.status_code)


def find_git_clone_code(url):
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser") #TODO hreflerden ayrış
    anahtar_kelime = "git clone --mirror"

    # HTML kodunu satır satır kontrol et
    for i, satir in enumerate(soup.get_text().split("\n")):
        satir = satir.replace("# oldest", "").replace(
            "# newest", ""
        )  # İfadeleri kaldır
        if anahtar_kelime in satir:
            code = satir.strip().replace("--mirror", "")
            print(code)  # TODO Gereksiz test amaçlı

            yield code  # Birden fazla git olursa ilkini alacak. #TODO



def git_clone(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)#usr

    if result.returncode == 0:
        output = result.stdout
        print("Komut çıktısı:\n", output)
    else:
        error = result.stderr
        print("Hata mesajı:\n", error)


def genel_site_indirme(url):  # url = "https://lore.kernel.org" #Bitmediiiiii !!!!
    response = requests.get(url)
    print(f"{url} indirildi.")
    soup = BeautifulSoup(response.content, "html.parser")

    links = soup.find_all("a")
    link_dict = {}
    while True:
        for link in links:
            link_text = link.text.strip()
            link_href = link.get("href")

            if type(find_mirror(url + "/" + link_href)) == str and link_text != "all":
                link_dict[link_text] = (
                    url + "/" + link_href + "/" + find_mirror(url + "/" + link_href)
                )
                git_clone(find_git_clone_code(link_dict[link_text]))

        if "next (older)" in link_dict:
            response = requests.get(link_dict["next (older)"])

        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a")

        if not "next (older)" in link_dict:
            break
        del link_dict["next (older)"]
    print(link_dict)  # TODO #Gereksiz test amaçlı


genel_site_indirme("https://lore.kernel.org")
