import requests
import re

triggers = ("wiktionary", "wt", "wikt")

# NOUN = "Noun"
# VERB = "Verb"
# ADJECTIVE = "Adjective"
# ADVERB = "Adverb"
# INTERJECTION = "Interjection"

# {
#     'word': { 'lang': {
#        'noun': ['def1', 'def2', 'def3'], 'verb': ['def1', 'def2', 'def3'] },
#            }
#     'word': { 'lang': { 
#        'noun': ['def1', 'def2', 'def3'], 'verb': ['def1', 'def2', 'def3'] },
#         },
# }

definitionsCache = dict()

# Return False for no results, True for successfully parsed and cached query
def wiktionaryCmd(word):
    word = word.lower()
    url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{word}"
    response = requests.get(url)
    if response.status_code != 200:
        return False
    data = response.json()
    global definitionsCache
    definitionsCache[word] = dict()
    for lang in data:
        if lang not in definitionsCache[word]:
            definitionsCache[word][lang] = { "_language": "" }
        for wordData in data[lang]:
            partOfSpeech = wordData["partOfSpeech"].lower()
            language = wordData["language"]
            definitionsCache[word][lang]["_language"] = language
            for defs in wordData["definitions"]:
                d = defs["definition"]
                d = re.sub("<.+?>", "", d)
                try:
                    definitionsCache[word][lang][partOfSpeech].append(d)
                except KeyError:
                    definitionsCache[word][lang][partOfSpeech] = [d]
    return True

def wiktionary(botObj, nick, target, params):
    if not params: return
    lang = "de" if target == "##deutsch" else "en"
    paramsCopy = params.copy()
    n = 1
    fetchMetadata = False
    for param in paramsCopy:
        if param in ("--metadata", "--mt"):
            # Only show the metadata for the word
            fetchMetadata = True
            params.pop(0)
            break
        if param.startswith("lang=") or param.startswith("l="):
            try:
                lang = param.split("=")[1]
            except IndexError:
                botObj.msg(target, "Error parsing input.")
                return
            params.pop(0)
        elif param.startswith("grammar=") or param.startswith("g="):
            try:
                partOfSpeech = param.split("=")[1]
            except IndexError:
                botObj.msg(target, "Error parsing input.")
                return
            params.pop(0)
        elif param.startswith("n="):
            try:
                i = int(param.split("=")[1])
            except (IndexError, ValueError):
                botObj.msg(target, "Error parsing input.")
                return
            n = i
            if i < 1:
                n = 1
            params.pop(0)

    word = "_".join(params).lower()
    definition = ""
    language = "English"
    partOfSpeech = "noun"
    defCount = 0
    message = ""
    if word not in definitionsCache:
        success = wiktionaryCmd(word)
        if not success:
            botObj.msg(target, "No results found.")
            return
    if fetchMetadata:
        # Only show the types of speech that are available to select from.
        for lang in definitionsCache[word]:
            message += f"{chr(2)}{definitionsCache[word][lang]['_language']} ({lang}):{chr(2)} "
            for grammarPart in definitionsCache[word][lang]:
                if grammarPart == "_language":
                    continue
                message += f"{grammarPart}: {len(definitionsCache[word][lang][grammarPart])}, "
    else:
        if lang not in definitionsCache[word]:
            lang = list(definitionsCache[word].keys())[0]
        if partOfSpeech not in definitionsCache[word][lang]:
            partOfSpeech = list(definitionsCache[word][lang].keys())[1]
        try:
            definition = definitionsCache[word][lang][partOfSpeech][n-1]
            language = definitionsCache[word][lang]["_language"]
            defCount = len(definitionsCache[word][lang][partOfSpeech])
            word = word.replace("_", " ")
            message = f"{chr(2)}{word}:{chr(2)} {language} / {partOfSpeech} ({n}/{defCount}): {definition}"
        except (KeyError, IndexError):
            botObj.msg(target, "Couldn't fetch definition according to supplied parameters.")
            return
    
    botObj.msg(target, message)

def help():
    msg = """Fetches the definition of a word from Wiktionary according to the given parameters.
Optional parameters: g=<noun/verb/adjective/adverb> n=N, lang=<language code name>.
Example input: ".wiktionary lang=en g=noun n=2 vegan" to fetch the second English noun definition for the word "vegan".
Aliases: wt, wikt."""
    return msg

if __name__ == "__main__":
    print(wiktionaryCmd("love"))
    print(wiktionaryCmd("Geist"))
else:
    def registerCommands():
        commands = {}
        for trigger in triggers:
            commands[trigger] = wiktionary
        return commands
