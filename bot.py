from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from datetime import datetime, timedelta
import os
import sys
import plugin # Plugin manager

class TitleBot(irc.IRCClient):
    def __init__(self):
        super().__init__()
        self.nickname = "vegbot" # Current nickname
        self.nickCollisionId = 0 # Increases in case of collision and gets attached to the nick
        self.baseNick = "vegbot" # Base nickname for the collision alter-nick function
        # Flood protection stuff
        self.lastMessageTimestamp = datetime.now() # When was the last message received
        self.linksCount = 0 # How many links we have handled within the last 10 seconds
        self.ignoreMessagesUntil = datetime.now() # Ignore messages due to flooding until this timestamp has passed
        self.admins = {"Trashlord", "rae", "xx", "krm", "tumble", "Roey", "simplicity"}

    def lineReceived(self, line):
        super().lineReceived(line)
        if self.factory.isTestMode:
            # Running in test mode, don't parse anything here, don't identify to SASL.
            return
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
        # This will only be executed if the bot isn't in test mode.
        if cmd == "CAP" and args == "ACK :sasl":
            # Continue with SASL authentication
            self.sendLine("AUTHENTICATE PLAIN")
        elif cmd == "903":
            self.sendLine("CAP END")
            # Join the channel
            print(f"SASL authentication complete. Joining {self.factory.channels}")
            self.join(self.factory.channels)

    def connectionMade(self):
        print("Connected to server...")
        super().connectionMade()
        if self.factory.isTestMode:
            # No SASL here.
            return
        self.sendLine("CAP REQ :sasl")

    def signedOn(self):
        if self.factory.isTestMode:
            print(f"Joining {self.factory.channels}")
            self.join(self.factory.channels)

    def userJoined(self, user, channel):
        plugin.dispatchEvent(plugin.E_JOIN, self, user, channel)
    
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
        plugin.dispatchEvent(plugin.E_PRIVMSG, self, nick, target, words) 
        
        # Handle commands
        if words[0].startswith(plugin.cmdChar) and len(words[0]) > 1:
            cmd = words[0][1:].lower()
            params = words[1:]
            if cmd == "plugin" and nick in self.admins:
                # Only bot owner can mess with plugins - make this configurable
                self.handlePlugin(target, params)
            else:
                self.isFlood()
                plugin.dispatchCommand(cmd, self, nick, target, params)
 
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

    def handlePlugin(self, target, params):
        # target is for output
        if not params:
            return
        action = params.pop(0)
        if action == "load":
            if not params:
                # Load everything
                success = plugin.findPlugins()
                if success:
                    self.msg(target, "Loaded all plugins.")
                else:
                    self.msg(target, "Not all plugins loaded.")
            else:
                # Load the specific plugin
                name = params.pop(0)
                success = plugin.loadPlugin(name)
                if success:
                    self.msg(target, f"Loaded plugin {name}.")
                else:
                    self.msg(target, f"Failed to load plugin {name}.")
        elif action == "unload":
            if not params:
                return
            name = params[0]
            success = plugin.unloadPlugin(name)
            if success:
                self.msg(target, f"Unloaded plugin {name}.")
        elif action == "reload":
            if not params:
                return
            name = params[0]
            success = plugin.reloadPlugin(name)
            if success:
                self.msg(target, f"Reloaded plugin {name}.")
            else:
                self.msg(target, f"Failed to reload plugin {name}.")

    def noticed(self, user, channel, message):
        print(f"NOTICE - <{user}> {message}")

    def alterCollidedNick(self, nickname):
        # Nickname collision.
        # if our nick is titlebot, it becomes titlebot1
        # if it's titlebot1, it becomes titlebot2, and so on.
        self.nickCollisionId += 1
        self.nickname = f"{self.baseNick}{self.nickCollisionId}"
        return self.nickname

class TitleBotFactory(protocol.ClientFactory):
    def __init__(self, channels: str, isTestMode: bool):
        self.channels = channels
        self.isTestMode = isTestMode
        if not isTestMode:
            self.password = os.environ["VEGBOT_PASSWORD"]
        # Load plugins
        plugin.findPlugins()

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
channels = "##vegan,##deutsch,##deutsch-offtopic,##metal,##eco"
testChannel = "##trashtest"
isTestMode = False

if len(sys.argv) > 1 and sys.argv[1] == "--test":
    print("Running in test mode...")
    channels = testChannel
    # Run the bot in Test mode. No SASL identification. Join the channels in the signedOn event.
    isTestMode = True

botFactory = TitleBotFactory(channels, isTestMode)

reactor.connectSSL(server, port, botFactory, ssl.ClientContextFactory())
reactor.run()
