import requests
import re

triggers = ("wiktionary", "wt", "wikt")

def wiktionary(params, target=None):
    word = "_".join(params)
    url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{word}"
    response = requests.get(url)
    if response.status_code != 200:
        return ("No results found.",)
    data = response.json()
    # Most basic for now
    d = data["en"][0]["definitions"][0]["definition"]
    d = re.sub("<.+?>", "", d)
    return (d,)

if __name__ == "__main__":
    print(wiktionary(["love"]))
else:
    from commands import addCommand
    addCommand(triggers, wiktionary)
