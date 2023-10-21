# YouTube and URL title fetcher
import re
import requests
import subprocess
import json
from datetime import datetime
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
            getPageTitle(botObj, target, word)

youtubeTitles = dict()
titles = dict() # Normal URL

def getVideoInfo(url):
    # We use cURL for this one
    full_url = f"https://www.youtube.com/oembed?url={url}"
    try:
        response = subprocess.check_output(["curl", full_url])
    except subprocess.CalledProcessError as ex:
        print(f"Error fetching YouTube video info: {ex}")
        return (None, None)
    try:
        info = json.loads(response.decode())
    except json.decoder.JSONDecodeError as ex:
        print(f"JSON decoding error: {ex}")
        return (None, None)

    # All good here
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
            botObj.msg(target, "Error fetching YouTube video info.")
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


# curl -x GET "https://stackoverflow.com/questions/9445489/performing-http-requests-with-curl-using-proxy" --proxy "socks://127.0.0.1:9050"

def getPageTitle(botObj, target, url):
    global titles
    if url in titles:
        title = titles[url]
    else:
        try:
            content = subprocess.check_output(["curl", "-x", "GET", url, "--proxy", "socks://127.0.0.1:9050"])
        except subprocess.CalledProcessError as ex:
            print("Error retrieving page content")
            return
        soup = BeautifulSoup(content, "html.parser")
        if not soup.title:
            return

        title = " ".join(soup.title.string.split("\n"))
        if len(title) > 350:
            title = f"{title[:350]}..."
        titles[url] = title
    botObj.msg(target, f"{bold}Title:{bold} {title}")

def getUrlTitle(botObj, target, url):
    global titles
    if url in titles:
        title = titles[url]
    else:
        response = torRequest(url)
        if response is None or response.status_code != 200:
            print("--- HTTP REQUEST FAILED ---")
            print("Trying again...")
            response = requests.get(url)
            if response is None or response.status_code != 200:
                print("--- HTTP REQUEST FAILED ---")
                print("--- GIVING UP ---")
                return
            print("Success!")
        try:
            content = response.content.decode()
        except UnicodeDecodeError:
            print(f"{datetime.now()} UnicodeDecodeError for {url}")
            return
        soup = BeautifulSoup(content, "html.parser")
        if not soup.title:
            # None or empty
            return
        title = " ".join(soup.title.string.split("\n"))
        if len(title) > 350:
            title = f"{title[:350]}..."
        titles[url] = title
    botObj.msg(target, f"{bold}Title:{bold} {title}")

def dropYoutubeCaches(botObj, nick, target, params):
    global youtubeTitles
    youtubeTitles = {}
    botObj.msg(target, "YouTube caches dropped.")

if __name__ == "__main__":
    print(getVideoInfo("https://www.youtube.com/watch?v=_yROyxWcudo"))
    print(getVideoInfo("https://www.youtube.com/watch?v=j0_u26Vpb4w"))
else:
    from plugin import E_PRIVMSG
    from codes import bold
    def registerEvents():
        return {E_PRIVMSG: [parseMessage]}
    def registerCommands():
        return {"dropyoutube": dropYoutubeCaches}
