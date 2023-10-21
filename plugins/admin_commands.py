# Admin commands: join, leave
# TODO: stronger authentication

admins = {"Trashlord", "rae", "xx", "krm", "tumble"}

def handleJoin(botObj, nick, target, params):
    if not params:
        return
    if nick not in admins:
        return
    channel = params.pop(0)
    botObj.join(channel)

def handlePart(botObj, nick, target, params):
    if not params:
        return
    if nick not in admins:
        return
    channel = params.pop(0)
    botObj.leave(channel)

def handleKb(botObj, nick, target, params):
    if not params or target == botObj.nickname:
        return
    if nick not in admins:
        return
    knick = params.pop()
    botObj.mode(target, True, f"b {knick}")
    botObj.kick(target, knick, "bye")

def handleOpMe(botObj, nick, target, params):
    if nick not in admins:
        return
    if target == botObj.nickname:
        return
    botObj.mode(target, True, f"o {nick}")

def registerCommands():
    commands = dict()
    commands["join"] = handleJoin
    commands["part"] = handlePart
    commands["leave"] = handlePart
    commands["kb"] = handleKb
    commands["opme"] = handleOpMe
    return commands
