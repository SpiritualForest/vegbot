# Vegbot commands

cmdChar = "." # To trigger a command via message, use "<char>cmd" - such as ".cmd"

callbacks = dict() # trigger word: callback

def addCommand(triggers, function):
    print(f"addCommand({triggers}, {function}")
    global callbacks
    for trigger in triggers:
        callbacks[trigger] = function

def executeCommand(trigger: str, botObj, nick: str, target: str, params: list[str]):
    try:
        callback = callbacks[trigger]
    except KeyError:
        # No such command
        return
    callback(botObj, nick, target, params)
