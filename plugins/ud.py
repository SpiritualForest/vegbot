# Urban dictionary

import requests

bold = chr(2)

# term - definitions array
cache = {}

def udCmd(term, n = 0):
    global cache
    definition = None
    if term in cache and n < len(cache[term]):
        definition = cache[term][n]
    else:
        # Cache miss, let's fetch all defs
        url = f"http://api.urbandictionary.com/v0/define"
        content = requests.get(url, params={"term": term}, headers={"Referer": "http://m.urbandictionary.com"}).json()
        definitions = content["list"]
        if not definitions or n >= len(definitions):
            return "No results found."
        cache[term] = []
        for raw_definition in definitions:
            definition = raw_definition["definition"].replace("[", "").replace("]", "")
            definition = definition.split("\n").pop(0)
            cache[term].append(definition)
    definition = cache[term][n]
    return f"{bold}{term}{bold} ({n+1}/{len(cache[term])}): {definition[:300]}"

def ud(botObj, nick, target, params):
    if not params:
        return
    n = 1
    if len(params) > 1:
        if params[0].isdigit():
            n = int(params.pop(0))
            if n < 1:
                n = 1
    term = " ".join(params)
    botObj.msg(target, udCmd(term, n-1))

def registerCommands():
    return {"ud": ud}

def help():
    return ".ud <word> - fetches the definition of the given word."

if __name__ == "__main__":
    print(udCmd("shit"))
    print(udCmd("shit", 1))
    print(udCmd("shit", 5))
    print(udCmd("vegan", 11))
