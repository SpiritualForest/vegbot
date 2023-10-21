b = chr(2)
c = chr(3)

def _100percent(botObj, nick, target, params):
    fallacy = "Veganism is the philosophical position that exploitation of and cruelty  to sentient beings is ethically indefensible and should be avoided  whenever it is possible and practicable to do so. Vegans themselves do  not claim this position is absolute nor do they strive for perfection. Rather, the accusation that vegans fail to be vegan because they cannot  be perfect is an external one imposed by people who do not understand veganism."
    botObj.msg(target, fallacy)

def help():
    return "Displays the 100% fallacy"

def registerCommands():
    commands = dict()
    commands["100%"] = _100percent
    commands["100percent"] = _100percent
    commands["veganismdef"] = _100percent
    return commands
