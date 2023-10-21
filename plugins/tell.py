import redis
from datetime import datetime

# Command: .tell <user> <msg>
# When <user> next speaks anywhere, the bot sends: <user>: <sender> tells you: <msg>

r = redis.StrictRedis(host="127.0.0.1", port=6379, decode_responses=True)

def getMessageKey(user: str, msgId: int):
    return f"{user}:msg:{msgId}"

def tell(botObj, nick, target, params):
    # .tell <user> <msg>
    if len(params) < 2:
        # Need at least <user> and <msg>
        botObj.msg(target, f"{nick}: not enough parameters. Syntax: .tell <user> <message>")
        return
    user = params.pop(0)
    message = " ".join(params)
    tellCmd(nick, user, message)
    botObj.msg(target, f"{nick}: okay, I will pass that when {user} is around.")

def tellCmd(sender, user, message):
    # Redis keys
    user = user.lower()
    listKey = f"{user}:pending-messages"
    lastMsgId = r.lrange(listKey, -1, -1) # Get the last message ID, then we increase this value
    if not lastMsgId:
        # -1 if nothing was previously saved
        lastMsgId = -1
    else:
        lastMsgId = lastMsgId.pop()
    msgId = int(lastMsgId)+1
    msgKey = getMessageKey(user, msgId)

    # Append the ID to the pending messages list for the user
    r.rpush(listKey, msgId)
    
    # Add the whole message object to the dictionary
    utcnow = datetime.utcnow()
    h = "0" + str(utcnow.hour) if utcnow.hour < 10 else utcnow.hour
    m = "0" + str(utcnow.minute) if utcnow.minute < 10 else utcnow.minute
    s = "0" + str(utcnow.second) if utcnow.second < 10 else utcnow.second
    datetimeFormatted = f"{utcnow.year}/{utcnow.month}/{utcnow.day} {h}:{m}:{s}"
    msgDict = {"sender": sender, "user": user, "message": message, "time": datetimeFormatted}
    # Because hmset() is deprecated, we're going to use the correct hset() command instead
    for key in msgDict:
        val = msgDict[key]
        r.hset(msgKey, key, val)

def tellCallback(botObj, nick, target, params):
    # Called when <nick> sends a message
    messages = getUserMessages(nick)
    for message in messages:
        botObj.msg(target, message)

def getUserMessages(nick):
    nickLower = nick.lower()
    listKey = f"{nickLower}:pending-messages"
    messages = r.lrange(listKey, 0, -1)
    if not messages:
        # Do nothing
        return []
    replies = []
    for msgId in messages:
        msgId = int(msgId)
        msgKey = getMessageKey(nickLower, msgId)
        msgData = r.hgetall(msgKey)
        reply = f"{nick}: memo from {msgData['sender']} at {msgData['time']} UTC: {msgData['message']}"
        # Remove the message from the dictionary after processing it
        r.delete(msgKey)
        replies.append(reply)
    # Remove the pending messages list for <nick>
    r.delete(listKey)
    return replies

if __name__ == "__main__":
    # Trashlord sends memo to rae
    tellCmd("Trashlord", "rae", "You should watch this video.")
    # krm sends memo to rae
    tellCmd("krm", "rae", "I just wanted to let you know about this new video game.")
    tellCmd("krm", "RAE", "Another message.")
    # rae speaks in ##vegan
    replies = getUserMessages("rae")
    for reply in replies: print(reply)

else:
    from plugin import E_PRIVMSG
    def registerCommands():
        return {"tell": tell, "t": tell}
    def registerEvents():
        return {E_PRIVMSG: [tellCallback]}
    def help():
        return ".tell <nick> <message> - passes the message to the given username next time they speak anywhere."
