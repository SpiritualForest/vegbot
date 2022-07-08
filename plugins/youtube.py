# Fetches YouTube video titles and uploader name

import requests

titles = dict()

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
    global titles
    if url in titles:
        # The title for this particular URL was already fetched earlier and cached
        title, uploader = titles[url]
    else:
        # Not cached. Fetch new.
        title, uploader = getVideoInfo(url)
        if (title, uploader) == (None, None):
            # Bad URL
            return
        # Cache it
        titles[url] = (title, uploader)
        botObj.msg(target, f"{bold}Title{bold}: {title} ({bold}Uploader:{bold} {uploader})")

if __name__ == "__main__":
    print(getVideoInfo("https://www.youtube.com/watch?v=_yROyxWcudo"))
    print(getVideoInfo("https://www.youtube.com/watch?v=j0_u26Vpb4w"))
else:
    import events
    from codes import bold
