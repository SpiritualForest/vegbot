# Commands can hook events to execute their callbacks

E_PRIVMSG = "privmsg"

events = dict()

def addEvent(event, callback):
    try:
        events[event].append(callback)
    except KeyError:
        events[event] = [callback]

def executeCallbacks(event, botObj, nick, target, params):
    # Execute all the callback functions that hooked <event>
    for callback in events[event]:
        callback(botObj, nick, target, params)
