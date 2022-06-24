# Urban dictionary

import requests

def ud(term):
    url = f"http://api.urbandictionary.com/v0/define"
    content = requests.get(url, params={"term": term}, headers={"Referer": "http://m.urbandictionary.com"}).json()
    definitions = content["list"]
    if not definitions:
        return (None, None)
    return (definitions[0]["word"], definitions[0]["definition"].replace("[", "").replace("]", ""))

if __name__ == "__main__":
    w, d = ud("shit")
    if d is None:
        print("No results")
    print(f"{w}: {d[:350]}")
