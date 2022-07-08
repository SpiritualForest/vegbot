# This plugin only parses messages to check for titles.
from plugins import youtube
from plugins import url_title
import events
import re

urlGeneral = re.compile("^https?://.+\.[A-Za-z0-9]+/?.+?$")
ytPatternDotcom = re.compile("^https://(www|m).youtube.com/watch\?v=.+$")
ytPatternDotbe = re.compile("^https://youtu.be/.+$")

def parseMessage(botObj, nick, target, params):
    for word in params:
        if ytPatternDotcom.match(word) or ytPatternDotbe.match(word):
            # YouTube URL
            if botObj.isFlood():
                return
            youtube.youtube(botObj, target, word)
        elif urlGeneral.match(word):
            # Normal URL
            if botObj.isFlood():
                return
            url_title.getUrlTitle(botObj, target, word)

events.addEvent(events.E_PRIVMSG, parseMessage)
