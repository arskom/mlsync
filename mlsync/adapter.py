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
            return url+"/"+link_url
        else:
            print("Hedef metin için bağlantı bulunamadı.")
    else:
        print("Sayfa çekilemedi. Hata kodu:", response.status_code)


def find_git_clone_code(url,link_text):
    # Web sayfasını indirin
    response = requests.get(url)

    # İçeriği analiz etmek için BeautifulSoup kullanın
    soup = BeautifulSoup(response.content, "html.parser")

    # Verilen anahtar kelimeye sahip olan linkleri seçin ve döndürün
    for link in soup.find_all("a"):
        link_split = link.text.split("/")
        if link_text in link.text and len(link_split) == 5 and link_split[0:3] == ['http:', '', 'lore.kernel.org'] and link_split[-2] == link_text and link_split[-1].isdigit():
            yield link.get("href")

def git_clone(url):
    split_url = url.split("/")
    result = subprocess.run(["git " + "clone " + url + f" {split_url[-2]}/{split_url[-1]}"], shell=True,)#TODO komutun inputu link olacak ve target belirle !!!

    if result.returncode == 0:
        output = result.stdout
        print("Komut çıktısı:\n", output)
    else:
        error = result.stderr
        print("Hata mesajı:\n", error)


def genel_site_indirme(url):  # url = "https://lore.kernel.org" #Bitmediiiiii !!!!
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = soup.find_all("a")
    link_dict = {}
    while True:
        for link in links:
            link_text = link.text.strip()
            link_href = link.get("href")

            if type(find_mirror(url + "/" + link_href)) == str and link_text != "all":
                link_dict[link_text] = (find_mirror(url + "/" + link_href))
                a = find_git_clone_code(link_dict[link_text],link_text)
                print(link_dict)

                for i in a:
                    git_clone(i)

        if "next (older)" in link_dict:
            response = requests.get(link_dict["next (older)"])

        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a")

        if not "next (older)" in link_dict:
            break
        del link_dict["next (older)"]
    print(link_dict)  # TODO #Gereksiz test amaçlı


genel_site_indirme("https://lore.kernel.org")
