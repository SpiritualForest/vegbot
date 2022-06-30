import requests

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

if __name__ == "__main__":
    print(getVideoInfo("https://www.youtube.com/watch?v=_yROyxWcudo"))
    print(getVideoInfo("https://www.youtube.com/watch?v=j0_u26Vpb4w"))
