from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
import requests
from datetime import datetime, timedelta
import re
import os
import json
import sys
from bs4 import BeautifulSoup
from wikipedia import wikipedia # Our own plugin

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
        if target == self.nickname:
            # private to us, ignore for now
            return
        
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
        if words[0].startswith("."):
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
                    title, author = self.youtube[word]
                else:
                    # Not cached. Fetch new.
                    title, author = self.getYouTubeData(word)
                    if (title, author) == (None, None):
                        # Bad URL
                        return
                    # Cache it
                    self.youtube[word] = (title, author)
                self.msg(target, f"{bold}Title{bold}: {title} ({bold}Uploader:{bold} {author})")
            
            elif urlGeneral.match(word) is not None:
                # Regular URL title fetching
                if self.isFlood():
                    return
                if word in self.titles:
                    title = self.titles[word]
                else:
                    response = self.torRequest(word)
                    if response is None or response.status_code != 200:
                        return
                    content = response.content.decode()
                    soup = BeautifulSoup(content, "html.parser")
                    title = soup.title.string
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

    def torRequest(self, url):
        session = requests.session()
        session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
        try:
            response = session.get(url)
        except requests.exceptions.ConnectionError:
            response = None
        return response

    def getYouTubeData(self, url):
        response = self.torRequest(f"https://www.youtube.com/oembed?url={url}")
        if response is None or response.status_code != 200:
            return (None, None)
        json_data = json.loads(response.content.decode())
        return (json_data["title"], json_data["author_name"])

    def handleBotCommand(self, nick, cmd, args, channel):
        if nick in self.admins:
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
        if not args: return
        if cmd in ("wikipedia", "wiki", "w", "wp"):
            lang = "en"
            if args[0].startswith("l=") or args[0].startswith("lang="):
                lang = args[0].split("=").pop()
                args.pop(0)
            description, url = wikipedia(" ".join(args), lang)
            if url is None:
                self.msg(channel, description)
            else:
                self.msg(channel, description) 
                self.msg(channel, f"{chr(2)}{chr(3)}12{url}{chr(3)}{chr(2)}")

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