import random
answers = (
        # Positives
        ("It is certain.", "It is decidedly so.", "Without a doubt.", "Yes definitely.", "You may rely on it.",
         "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes."),
        # Non-committal
        ("Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again."),
        # Negatives
        ("Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful.", "No.")
        )

def getRandomAnswer():
    group = answers[random.randint(0, len(answers)-1)]
    return group[random.randint(0, len(group)-1)]

def eightBall(botObj, nick, target, params):
    if not params:
        return
    answer = getRandomAnswer()
    botObj.msg(target, f"{nick}: {answer}")

def registerCommands():
    commands = dict()
    commands["ask"] = eightBall
    commands["8ball"] = eightBall
    return commands

def help():
    return "ask a question and get a random answer from the Magic 8 Ball. Commmands: '.ask <question>' or '.8ball <question>'"

if __name__ == "__main__":
    for i in range(10):
        print(getRandomAnswer())
