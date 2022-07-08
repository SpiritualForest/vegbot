import requests
import re

triggers = ("wiktionary", "wt", "wikt")

def wiktionaryCmd(word):
    url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{word}"
    response = requests.get(url)
    if response.status_code != 200:
        return "No results found."
    data = response.json()
    # Most basic for now
    d = data["en"][0]["definitions"][0]["definition"]
    d = re.sub("<.+?>", "", d)
    return d

def wiktionary(botObj, nick, target, params):
    if not params: return
    word = "_".join(params)
    definition = wiktionaryCmd(word)
    botObj.msg(target, definition)

if __name__ == "__main__":
    print(wiktionaryCmd("love"))
else:
    def registerCommands():
        commands = {}
        for trigger in triggers:
            commands[trigger] = wiktionary
        return commands
