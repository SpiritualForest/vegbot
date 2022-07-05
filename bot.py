from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os
import sys
import commands
import events
from tor_request import torRequest
from plugins import wikipedia, wiktionary, youtube, ud, calc, tell, seen

urlPatternDotcom = re.compile("^https://(www|m).youtube.com/watch\?v=.+$")
urlPatternDotbe = re.compile("^https://youtu.be/.+$")
urlGeneral = re.compile("^https?://.+\.[A-Za-z0-9]+/?.+?$")

class TitleBot(irc.IRCClient):
    def __init__(self):
        super().__init__()
        self.nickname = "vegbot" # Current nickname
        self.nickCollisionId = 0 # Increases in case of collision and gets attached to the nick
        self.baseNick = "vegbot" # Base nickname for the collision alter-nick function
        self.youtube = dict() # url: (title, author) for memoization
        self.titles = dict() # url: title
        # Flood protection stuff
        self.lastMessageTimestamp = datetime.now() # When was the last message received
        self.linksCount = 0 # How many links we have handled within the last 10 seconds
        self.ignoreMessagesUntil = datetime.now() # Ignore messages due to flooding until this timestamp has passed
        self.admins = {"Trashlord", "rae", "xx", "krm", "tumble"}

    def lineReceived(self, line):
        super().lineReceived(line)
        line = line.decode()
        chunks = line.split()
        # :zinc.libera.chat CAP vegbot2 ACK :sasl
        if chunks[0] == f":{self.hostname}":
            cmd = chunks[1]
            args = " ".join(chunks[3:])
            self.serverReplied(cmd, args)
        elif line == "AUTHENTICATE +":
            # Server tells us to proceed with sending our base64 string
            b64 = self.factory.password
            self.sendLine(f"AUTHENTICATE {b64}")

    def serverReplied(self, cmd, args):
        if cmd == "CAP" and args == "ACK :sasl":
            # Continue with SASL authentication
            self.sendLine("AUTHENTICATE PLAIN")
        elif cmd == "903":
            self.sendLine("CAP END")
            # Join the channel
            print(f"SASL authentication complete. Joining {self.factory.channels}")
            self.join(self.factory.channels)

    def connectionMade(self):
        super().connectionMade()
        print("Connected to server...")
        # SASL stuff
        self.sendLine("CAP REQ :sasl")

    def signedOn(self):
        pass

    def privmsg(self, user, target, message):
        # If we reached here, it must be a channel message
        nick, host = user.split("!")
        print(f"<{nick}/{target}> {message}")
        
        # Flood protection
        if (self.ignoreMessagesUntil - datetime.now()).total_seconds() > 0:
            if nick not in self.admins:
                # Due to flooding we ignore messages now
                print("Ignoring message due to flooding")
                return

        words = message.split()
        if target == self.nickname:
            # if pm, the output target becomes the user
            target = nick
        
        # Execute the privmsg event callbacks
        events.executeCallbacks(events.E_PRIVMSG, self, nick, target, words) 
        
        # Handle commands
        if words[0].startswith(commands.cmdChar) and len(words[0]) > 1:
            cmd = words[0][1:].lower()
            params = words[1:]
            self.handleBotCommand(nick, words[0][1:], params, target)
            return

        bold = chr(2)

        for word in words:
            # Use regex matching
            if urlPatternDotcom.match(word) is not None or urlPatternDotbe.match(word) is not None:
                if self.isFlood():
                    # Flooding detected
                    return
                if word in self.youtube:
                    # The title for this particular URL was already fetched earlier and cached
                    title, uploader = self.youtube[word]
                else:
                    # Not cached. Fetch new.
                    title, uploader = youtube.getVideoInfo(word)
                    if (title, uploader) == (None, None):
                        # Bad URL
                        return
                    # Cache it
                    self.youtube[word] = (title, uploader)
                self.msg(target, f"{bold}Title{bold}: {title} ({bold}Uploader:{bold} {uploader})")
            
            elif urlGeneral.match(word) is not None:
                # Regular URL title fetching
                if self.isFlood():
                    return
                if word in self.titles:
                    title = self.titles[word]
                else:
                    response = torRequest(word)
                    if response is None or response.status_code != 200:
                        print("--- HTTP REQUEST FAILED ---")
                        return
                    try:
                        content = response.content.decode()
                    except UnicodeDecodeError:
                        print(f"{datetime.now()} UnicodeDecodeError for {word}")
                        return
                    soup = BeautifulSoup(content, "html.parser")
                    title = " ".join(soup.title.string.split("\n"))
                    self.titles[word] = title
                self.msg(target, f"{bold}Title:{bold} {title}")
             
    def isFlood(self):
        # Flooding detection
        timespan = datetime.now() - self.lastMessageTimestamp
        self.linksCount += 1
        if timespan.total_seconds() < 10:
            if self.linksCount == 4:
                # Less than 10 seconds passed between messages that contain YouTube urls
                # We will only handle up to 4 url fetches in 10 seconds, so
                # set the bot to ignore further messages for the next 30 seconds.
                self.ignoreMessagesUntil = datetime.now() + timedelta(seconds=30)
                return True
        else:
            print("Resetting counters")
            # More than 10 seconds since last message received, no flood occurred by our definition.
            # Reset counters.
            self.lastMessageTimestamp = datetime.now()
            self.linksCount = 0
            return False


    def noticed(self, user, channel, message):
        print(f"NOTICE - <{user}> {message}")

    def alterCollidedNick(self, nickname):
        # Nickname collision.
        # if our nick is titlebot, it becomes titlebot1
        # if it's titlebot1, it becomes titlebot2, and so on.
        self.nickCollisionId += 1
        self.nickname = f"{self.baseNick}{self.nickCollisionId}"
        return self.nickname

    def handleBotCommand(self, nick, cmd, args, target):
        if nick in self.admins:
            # Admin-only commands
            if cmd == "droptitles":
                # Drop title caches
                self.titles = dict()
                self.msg(channel, "Title caches dropped.")
            elif cmd == "dropyoutube":
                # Drop youtube data caches
                self.youtube = dict()
                self.msg(channel, "YouTube caches dropped.")
            elif cmd == "join":
                if not args: return
                self.join(",".join(args))
            elif cmd == "leave":
                if not args: return
                self.part(",".join(args))
        # Regular non-admin commands
        if self.isFlood():
            # Flooding detected.
            return
        if cmd == "help":
            # FIXME: handle this shit
            self.msg(channel, "Available commands: tell, seen, calc, wp, ud, join, leave, droptitles, dropyoutube")
        
        if not args:
            return
        if cmd in commands.callbacks:
            commands.executeCommand(cmd, self, nick, target, args)

class TitleBotFactory(protocol.ClientFactory):
    def __init__(self, channels):
        self.channels = channels
        self.password = os.environ["VEGBOT_PASSWORD"]

    def buildProtocol(self, addr):
        p = TitleBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        print(f"Disconnected: {reason}")
        print("Reconnecting...")
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print(f"Connection failed: {reason}")
        reactor.stop()

server = "irc.libera.chat"
port = 6697
channels = "##vegan,##deutsch,##metal"
testChannel = "##trashtest"

if len(sys.argv) > 1 and sys.argv[1] == "--test":
    channels = testChannel

botFactory = TitleBotFactory(channels)

reactor.connectSSL(server, port, botFactory, ssl.ClientContextFactory())
reactor.run()
