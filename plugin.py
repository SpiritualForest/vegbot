# Manage plugins

import importlib
import os

loadedPlugins = dict() # name: Plugin object
# When a plugin is loaded, its module object is placed into the reload list.
# This is so that in case the plugin is ever unloaded, and then loaded again, loadPlugin()
# will instruct importlib to use reload(moduleObj) instead of import_module("plugin name")
reload = []
pluginsDir = "plugins"
events = dict() # event: list of plugin objects who registered this event
commands = dict() # cmd: plugin who registered it

cmdChar = "."
E_PRIVMSG = "PRIVMSG"

class Plugin:
    def __init__(self, name, module, registeredCommands, registeredEvents):
        self.name = name
        self.module = module # The plugin module object / namespace
        self.commands = registeredCommands # dictionary: cmd name, callback func
        self.events = registeredEvents # dictionary: event name, callback func
        
        # Now register the commands and events of this plugin
        global commands, events
        for command in registeredCommands:
            if command in commands:
                # Already registered
                print(f"Plugin '{name}' can't register command '{command}': it is already registered.")
                continue
            commands[command] = name
        for event in registeredEvents:
            try:
                events[event].append(name)
            except KeyError:
                events[event] = [name]

    def dispatchEvent(self, event, botObj, nick, target, params):
        for func in self.events[event]:
            func(botObj, nick, target, params)

    def dispatchCommand(self, command, botObj, nick, target, params):
        func = self.commands[command]
        func(botObj, nick, target, params)

def findPlugins():
    for root, dirs, files in os.walk(pluginsDir):
        if root == pluginsDir:
            # Where our plugins live
            break
    
    # Now we parse the plugin name and load it
    for filename in files:
        filename = filename.replace(".py", "")
        success = loadPlugin(filename)
        if success:
            print(f"Plugin '{filename}' loaded successfully.")
        else:
            # Not all plugins loaded successfully, so return False
            return False
    # All loaded
    return True

def loadPlugin(name: str):
    name = f"{pluginsDir}.{name}"
    try:
        pluginModule = importlib.import_module(name)
        if pluginModule in reload:
            # Reload
            pluginModule = importlib.reload(pluginModule)
    except ModuleNotFoundError:
        print(f"Error loading plugin {name}: no such module")
        return False
    
    # Loaded successfully, now we need to call our events and commands registration function
    # It returns a tuple of dictionaries
    try:
        registeredCommands = pluginModule.registerCommands()
    except AttributeError:
        # No commands were registered by the plugin
        registeredCommands = {}
    try:
        registeredEvents = pluginModule.registerEvents()
    except AttributeError:
        # No events were registered by the plugin
        registeredEvents = {}
    pluginObj = Plugin(name, pluginModule, registeredCommands, registeredEvents)
    loadedPlugins[name] = pluginObj
    if pluginModule not in reload:
        reload.append(pluginModule)
    return True

def reloadPlugin(name: str):
    # Unload first
    if not unloadPlugin(name):
        print(f"Plugin {name} was never loaded.")
        return False
    # Now reload it
    reloaded = loadPlugin(name)
    if reloaded:
        return True
    else:
        # Reloading failed
        return False

def unloadPlugin(name: str):
    pluginName = f"{pluginsDir}.{name}"
    if pluginName not in loadedPlugins:
        # No such plugin
        return False
    # Remove the plugin from registered event and command callbacks
    global events, commands
    # list(...) to extract the keys as a list
    for e in list(events):
        if pluginName in events[e]:
            events[e].remove(pluginName)
    for c in list(commands):
        if commands[c] == pluginName:
            del commands[c]
    # Now remove the plugin's name from the loaded plugins dict
    del loadedPlugins[pluginName]
    return True

def dispatchEvent(event, botObj, nick, target, params):
    if event not in events:
        # Nobody registered this.
        return
    for pluginName in events[event]:
        pluginObj = loadedPlugins[pluginName]
        pluginObj.dispatchEvent(event, botObj, nick, target, params)

def dispatchCommand(command, botObj, nick, target, params):
    if command not in commands:
        # No plugin registered this command
        return
    pluginName = commands[command]
    pluginObj = loadedPlugins[pluginName]
    pluginObj.dispatchCommand(command, botObj, nick, target, params)

if __name__ == "__main__":
    # Test
    from time import sleep
    findPlugins()
    sleep(1)
    success = unloadPlugin("calc")
    if success: print("Unloaded calc")
    print("calc" in commands)
    # Now unload seen
    sleep(1)
    if unloadPlugin("seen"): print("Unloaded seen")
    print("seen" in commands)
    print("plugins.seen" in events[E_PRIVMSG])
    success = reloadPlugin("tell")
    if success:
        print("Reloaded plugin tell")

