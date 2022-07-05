# Code based on https://github.com/TotallyNotRobots/CloudBot/blob/main/plugins/wikipedia.py

import requests
from requests import RequestException

def getInfo(title, lang="en"):
    title = title.replace(" ", "_")
    summaryUrl = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
    with requests.get(summaryUrl) as response:
        return response.json()

def wiki(botObj, nick, target, params):
    lang = "de" if target == "##deutsch" else "en"
    if params[0].startswith("lang=") or params[0].startswith("l="):
        lang = params[0].split("=").pop()
        params.pop(0)
    text = " ".join(params)
    replies = wikipedia(text, lang)
    if len(replies) == 1:
        # Means no results found
        botObj.msg(target, "No results found.")
    else:
        description, url = replies
        botObj.msg(target, description)
        botObj.msg(target, f"{codes.bold}{codes.color}12{url}{codes.color}{codes.bold}")

def wikipedia(text, lang):
    searchUrl = f"http://{lang}.wikipedia.org/w/api.php?action=query&format=json&list=search"
    searchParams = { "srsearch": text.strip() }
    try:
        with requests.get(searchUrl, params=searchParams) as response:
            response.raise_for_status()
            data = response.json()
    except RequestException:
        return ("Could not get Wikipedia page.",)
    
    for result in data["query"]["search"]:
        title = result["title"]
        info = getInfo(title, lang)
        if info["type"] != "standard":
            continue

        description = info["extract"]
        url = info["content_urls"]["desktop"]["page"]
        break
    else:
        return ("No results found",)
    
    if len(description) >= 350:
        description = f"{description[:350]}..."

    return (description, f"{url}")

if __name__ == "__main__":
    result = wikipedia("cold brew", "en")
    for r in result: print(r)
    result = wikipedia("הלסינקי", "he")
    for r in result: print(r)
else:
    from commands import addCommand
    import codes
    addCommand(("w", "wiki", "wp", "wikipedia"), wiki) 
