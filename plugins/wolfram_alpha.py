import wolframalpha

app_id = "Enter ID here"

def wolfram(query):
    client = wolframalpha.Client(app_id)
    res = client.query(query)
    results = []
    for i, pod in enumerate(res.pods):
        for subpod in pod.subpods:
            results.append(subpod.plaintext)
            if i == 1:
                # End
                return results

def wa(botObj, nick, target, params):
    response = wolfram(" ".join(params))
    if response is None:
        botObj.msg(target, "No results.")
        return
    conversion, result = response
    b = chr(2)
    botObj.msg(target, f"{conversion}: {b}{result}{b}")

def registerCommands():
    return {"wa": wa}

def help():
    return ".wa <query> - queries the WolframAlpha API and returns the result."

if __name__ == "__main__":
    print(wolfram("35 kg to lbs"))
    print(wolfram("100 R to C"))
