# Converts between various units
import re

# Mass

M_OZ = "ounce"
M_G = "gram"
M_LB = "pound"
M_KG = "kg"

massUnits = {
        M_OZ: {
            M_G: 28.34952,
            M_KG: 0.02834952001,
            M_LB: 0.0625
            },
        M_G: {
            M_KG: 0.001,
            M_LB: 0.002204623,
            M_OZ: 0.03527396
            },
        M_LB: {
            M_KG: 0.4535924,
            M_G: 453.5924,
            M_OZ: 16
            },
        M_KG: {
            M_G: 1000,
            M_LB: 2.204623,
            M_OZ: 35.27396
            }
        }

# Temperature

T_CELS = "celsius"
T_FAHR = "fahrenheit"
T_KELV = "kelvin"

def c2f(n): return ((9 / 5) * n) + 32
def c2k(n): return n+273.15
def f2c(n): return (5 / 9) * (n - 32)
def f2k(n): return f2c(n)+273.15
def k2c(n): return n-273.15
def k2f(n): return 1.8 * (n - 273.15) + 32

temperatureConversion = {
        "fc": f2c,
        "cf": c2f,
        "fk": f2k,
        "ck": c2k,
        "kf": k2f,
        "kc": k2c,
        }
unitMatch = re.compile("^(-?\d*\.?\d*)°?(.*)$")

def convert(botObj, nick, target, params):
    message = "".join(params)
    result = parseMessage(message)
    if result:
        botObj.msg(target, f"{nick}: {result}")

def parseMessage(message):
    if "->" not in message:
        return
    parts = message.split("->")
    if len(parts) != 2:
        # Error
        return
    first, second = parts
    first = unitMatch.search(first)
    if not first:
        # Error parsing the first operand
        return
    # Now find which units we need to convert to and from.
    # For now, only temperature is supported
    firstValue, firstUnit = first.groups()
    firstUnit = firstUnit.strip().lower()
    second = second.strip().lower()
    if second.startswith("°"):
        second = second[1:]
    if firstUnit not in tuple("cfk") or second not in tuple("cfk"):
        # Not temperature units.
        return
    units = firstUnit+second
    return convertTemperature(float(firstValue), units)

def convertTemperature(n: float, units: str):
    result = n
    if units[0] != units[1]:
        function = temperatureConversion[units]
        result = round(function(n), 2)
    unit = units[-1].upper()
    if unit == "K":
        return f"{result} {unit}"
    return f"{result}°{units[-1].upper()}"

def registerCommands():
    return {"tempconv": convert}

def help():
    return ".tempconv <N1> -> <N2>. Example inputs: 25C -> F, 0 F -> K, 122 F -> C. Available units: C, F, K."

if __name__ == "__main__":
    print(parseMessage("5 C -> F"))
    print(parseMessage("22C -> K"))
    print(parseMessage("17 F -> C"))
    print(parseMessage("0C -> F"))
    print(parseMessage("test -> lol"))
    print(parseMessage("test ->"))
    print(parseMessage("0C -> K"))
    print(parseMessage("0K -> C"))
