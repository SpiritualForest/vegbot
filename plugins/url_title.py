# Fetches URL titles
import requests
from codes import bold
from bs4 import BeautifulSoup

def torRequest(url):
    session = requests.session()
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    try:
        response = session.get(url)
    except requests.exceptions.ConnectionError:
        print("torRequest() Connection error")
        response = None
    return response

titles = dict()

def getUrlTitle(botObj, target, url):
    global titles
    if url in titles:
        title = titles[url]
    else:
        response = torRequest(url)
        if response is None or response.status_code != 200:
            print("--- HTTP REQUEST FAILED ---")
            return
        try:
            content = response.content.decode()
        except UnicodeDecodeError:
            print(f"{datetime.now()} UnicodeDecodeError for {word}")
            return
        soup = BeautifulSoup(content, "html.parser")
        if not soup.title:
            # None or empty
            return
        title = " ".join(soup.title.string.split("\n"))
        titles[url] = title
    botObj.msg(target, f"{bold}Title:{bold} {title}")
