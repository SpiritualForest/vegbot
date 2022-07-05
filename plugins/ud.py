# Urban dictionary

import requests
from codes import bold
from commands import addCommand

def udCmd(term):
    url = f"http://api.urbandictionary.com/v0/define"
    content = requests.get(url, params={"term": term}, headers={"Referer": "http://m.urbandictionary.com"}).json()
    definitions = content["list"]
    if not definitions:
        return "No results found."
    word = definitions[0]["word"]
    definition = definitions[0]["definition"].replace("[", "").replace("]", "")
    definition = definition.split("\n").pop(0)
    return f"{bold}{word}{bold}: {definition[:300]}"

def ud(botObj, nick, target, params):
    if not params:
        return
    term = " ".join(params)
    botObj.msg(target, udCmd(term))

addCommand(("ud",), ud)

if __name__ == "__main__":
    result = udCmd("shit")
    for r in result: print(r)
