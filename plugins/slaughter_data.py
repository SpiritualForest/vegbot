def slaughter_data(botObj, nick, target, params):
    botObj.msg(target, "How many animals are slaughtered each day: https://ourworldindata.org/how-many-animals-get-slaughtered-every-day")

def registerCommands():
    return {
            "slaughter_data": slaughter_data,
            "sld": slaughter_data,
            }
