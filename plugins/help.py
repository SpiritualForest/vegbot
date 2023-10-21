# .help <plugin>
from plugin import helpMessages, pluginsDir, loadedPlugins

def displayHelp(botObj, nick, target, params):
    bold = chr(2)
    if not params:
        # Display all plugins instead
        rawPlugins = list(loadedPlugins)
        results = []
        for p in rawPlugins:
            results.append(p.split(".").pop())
        results = ", ".join(results)
        botObj.msg(target, f"Available plugins: {results}")
        return
    name = params.pop(0)
    pname = f"{pluginsDir}.{name}"
    if pname not in helpMessages:
        botObj.msg(target, f"No help listed for {name}.")
        return
    # Found the message
    botObj.msg(target, f"{bold}{name}{bold}: {helpMessages[pname]}")

def help():
    return "Syntax: .help <command> - displays a help message about the given command."

def registerCommands():
    return {"help": displayHelp}
