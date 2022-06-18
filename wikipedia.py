# Code based on https://github.com/TotallyNotRobots/CloudBot/blob/main/plugins/wikipedia.py

import requests
from requests import RequestException

def getInfo(title, lang="en"):
    title = title.replace(" ", "_")
    summaryUrl = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
    with requests.get(summaryUrl) as response:
        return response.json()

def wikipedia(text, lang="en"):
    searchUrl = f"http://{lang}.wikipedia.org/w/api.php?action=query&format=json&list=search"
    searchParams = { "srsearch": text.strip() }
    try:
        with requests.get(searchUrl, params=searchParams) as response:
            response.raise_for_status()
            data = response.json()
    except RequestException:
        return ("Could not get Wikipedia page.", None)
    
    for result in data["query"]["search"]:
        title = result["title"]
        info = getInfo(title, lang)
        if info["type"] != "standard":
            continue

        description = info["extract"]
        url = info["content_urls"]["desktop"]["page"]
        break
    else:
        return ("No results found", None)
    
    if len(description) >= 350:
        description = f"{description[:350]}..."

    return (description, url)

if __name__ == "__main__":
    desc, url = wikipedia("cold brew")
    print(desc, url)
    desc, url = wikipedia("הלסינקי", lang="he")
    print(desc, url)
