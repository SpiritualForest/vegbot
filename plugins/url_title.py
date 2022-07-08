# YouTube and URL title fetcher
import re
import requests
from bs4 import BeautifulSoup

urlGeneral = re.compile("^https?://.+\.[A-Za-z0-9]+/?.+?$")
ytPatternDotcom = re.compile("^https://(www|m).youtube.com/watch\?v=.+$")
ytPatternDotbe = re.compile("^https://youtu.be/.+$")

def parseMessage(botObj, nick, target, params):
    for word in params:
        if ytPatternDotcom.match(word) or ytPatternDotbe.match(word):
            # YouTube URL
            if botObj.isFlood():
                return
            youtube(botObj, target, word)
        elif urlGeneral.match(word):
            # Normal URL
            if botObj.isFlood():
                return
            getUrlTitle(botObj, target, word)

youtubeTitles = dict()
titles = dict() # Normal URL

def getVideoInfo(url):
    session = requests.session()
    session.proxies = {"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"}
    try:
        response = session.get(f"https://www.youtube.com/oembed?url={url}")
    except requests.exceptions.ConnectionError:
        return (None, None)
    if response.status_code != 200:
        # Some error
        print(f"Error fetching YouTube video info: {response.status_code}")
        return
    info = response.json()
    return (info["title"], info["author_name"])

def youtube(botObj, target, url):
    global youtubeTitles
    if url in youtubeTitles:
        # The title for this particular URL was already fetched earlier and cached
        title, uploader = youtubeTitles[url]
    else:
        # Not cached. Fetch new.
        title, uploader = getVideoInfo(url)
        if (title, uploader) == (None, None):
            # Bad URL
            return
        # Cache it
        youtubeTitles[url] = (title, uploader)
        botObj.msg(target, f"{bold}Title{bold}: {title} ({bold}Uploader:{bold} {uploader})")

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

if __name__ == "__main__":
    print(getVideoInfo("https://www.youtube.com/watch?v=_yROyxWcudo"))
    print(getVideoInfo("https://www.youtube.com/watch?v=j0_u26Vpb4w"))
else:
    from plugin import E_PRIVMSG
    from codes import bold
    def registerEvents():
        return {E_PRIVMSG: [parseMessage]}
