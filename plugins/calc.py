import subprocess

def calc(botObj, nick, target, params):
    expression = "".join(params)
    botObj.msg(target, f"{nick}: {calcCmd(expression)}")

def calcCmd(expression):
    try:
        result = subprocess.check_output(["calc", expression])
    except subprocess.CalledProcessError:
        return "Calculation error."
    result = result.decode().strip()
    if len(result) > 350:
        return "Result too long."
    return result

def help():
    return ".calc <expression> - calculates the expression and displays the result."

def registerCommands():
    return {"calc": calc}

if __name__ == "__main__":
    print(calcCmd("1+2"))
    print(calcCmd("(34*100)/521"))
    print(calcCmd("239847203987**892"))
