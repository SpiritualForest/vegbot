import subprocess

def calc(botObj, nick, target, params):
    expression = "".join(params)
    botObj.msg(target, calcCmd(expression))

def calcCmd(expression):
    try:
        result = subprocess.check_output(["calc", expression])
    except subprocess.CalledProcessError:
        return "Calculation error."
    result = result.decode().strip()
    if len(result) > 350:
        return "Result too long."
    return result

if __name__ == "__main__":
    print(calcCmd("1+2"))
    print(calcCmd("(34*100)/521"))
    print(calcCmd("239847203987**892"))
else:
    import commands
    commands.addCommand(("calc",), calc)
