# .seen <user>
import redis
import datetime

r = redis.StrictRedis(host="127.0.0.1", port=6379, decode_responses=True)

def seen(botObj, nick, target, params):
    if len(params) != 1:
        botObj.msg(target, "Syntax: .seen <user>")
        return
    user = params[0]
    botObj.msg(target, getLastSeen(user))

def getLastSeen(user):
    mapping = f"seen:{user.lower()}"
    data = r.hgetall(mapping)
    if not data:
        return f"I have never seen {user}."
    # Now for the actual stuff.
    nick = data["nick"]
    message = data["message"]
    channel = data["channel"]
    time = data["time"]
    # Construct the datetime object - everything is in UTC
    dtObj = datetime.datetime(
            int(data["year"]), int(data["month"]), int(data["day"]),
            int(data["hour"]), int(data["minute"]), int(data["second"])
            )
    timeDiff = datetime.datetime.utcnow() - dtObj # Is a timedelta object
    weeks, days = divmod(timeDiff.days, 7)
    minutes, seconds = divmod(timeDiff.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    reply = f"I have last seen {nick} "
    if weeks > 0:
        wmsg = "weeks" if weeks > 1 else "week"
        reply += f"{weeks} {wmsg} "
    if days > 0:
        dmsg = "days" if days > 1 else "day"
        reply += f"{days} {dmsg} "
    if hours > 0:
        hmsg = "hours" if hours > 1 else "hour"
        reply += f"{hours} {hmsg} "
    if minutes > 0:
        mmsg = "minutes" if minutes > 1 else "minute"
        reply += f"{minutes} {mmsg} "
    if seconds > 0:
        smsg = "seconds" if seconds > 1 else "second"
        reply += f"{seconds} {smsg} "
    # Yes, I know this is ugly, forgive me for now.
    elif (weeks, days, hours, minutes, seconds) == (0, 0, 0, 0, 0):
        reply += "0 seconds "
    reply += f"ago at {time} UTC, in {channel}, saying: {message}"
    return reply

# PRIVMSG event callback - simply logs the user's last message
def seenPrivmsg(botObj, nick, target, params):
    # Log <nick>'s last message
    msg = " ".join(params)
    utcnow = datetime.datetime.utcnow()
    logMessage(nick, target, msg, utcnow)

def logMessage(nick, channel, message, utcnow):
    mapping = f"seen:{nick.lower()}"
    # Formatted time
    h = utcnow.hour if utcnow.hour > 9 else "0" + str(utcnow.hour)
    m = utcnow.minute if utcnow.minute > 9 else "0" + str(utcnow.minute)
    s = utcnow.second if utcnow.second > 9 else "0" + str(utcnow.second)
    formattedUtcNow = f"{utcnow.year}/{utcnow.month}/{utcnow.day} {h}:{m}:{s}"
    r.hset(mapping, "time", formattedUtcNow)
    r.hset(mapping, "message", message)
    r.hset(mapping, "channel", channel)
    r.hset(mapping, "nick", nick)
    # for timedelta stuff
    r.hset(mapping, "year", utcnow.year)
    r.hset(mapping, "month", utcnow.month)
    r.hset(mapping, "day", utcnow.day)
    r.hset(mapping, "hour", utcnow.hour)
    r.hset(mapping, "minute", utcnow.minute)
    r.hset(mapping, "second", utcnow.second)

if __name__ == "__main__":
    # Test
    from time import sleep
    print(getLastSeen("Trashlord"))
    twoWeeks = datetime.timedelta(weeks=2, days=1, hours=5, minutes=29, seconds=40)
    logMessage("Trashlord", "##vegan", "this is a test message for seen plugin.", datetime.datetime.utcnow() - twoWeeks)
    sleep(2)
    print(getLastSeen("Trashlord"))
    logMessage("tRAshlOrD", "##vegan", "this is another test message", datetime.datetime.utcnow() - twoWeeks)
    print(getLastSeen("traSHLoRd"))
else:
    # Register the commands and privmsg event
    from plugin import E_PRIVMSG
    def registerCommands():
        return {"seen": seen, "s": seen}
    
    def registerEvents():
        return {E_PRIVMSG: [seenPrivmsg]}
