import subprocess
import commands

def calc(params, target=None):
    expression = "".join(params)
    try:
        result = subprocess.check_output(["calc", expression])
    except subprocess.CalledProcessError:
        return ("Calculation error.",)
    return (result.decode().strip(),)

commands.addCommand(("calc",), calc)

if __name__ == "__main__":
    print(calc(["1+2"]))
    print(calc(["(34*100)/521"]))
