
from Hidden_code import *
import sys, math, os
import numpy as np

from timeout import timeout, TimeoutError

time = int(os.getenv("TIMEOUT",60*3))


def intro():
    print("")
    print("      |")
    print("    \ | /")
    print("     \*/")
    print("  --**O**-- ")
    print("     /*\           PROBLEMS ARE MOUNTING")
    print("    / | \ ")
    print("      |")
    print("      ")
    print("      ")
    print("               __                                     __ ")
    print("              |\ \            ___________,           |\ \ ")
    print("              | \ \          |`           \          | \ \ ")
    print("              |  \ \         | `           \         |  \ \ ")
    print("              |   | |_________  `           \________|  | |")
    print("              |   | |__________) +-----------+________) | |")
    print("              |   | |        |   :           :       |  | |")
    print("              |   | |        |   :           :       |  | |")
    print("              |   | |        `   :           :       |  | |")
    print("              |   | |         `  :           :       |  | |")
    print("               \  | |          ` :           :        \ | |")
    print("                \ | |           `:___________>         \| |")
    print("                  --                                    --")
    print("")


def out(s:str):
    sys.stdout.write(s)
    sys.stdout.flush()

def log(s:str):
    sys.stderr.write(f"+ {s}")
    sys.stderr.flush()

def setup():
    pass

def toFloat(s:str):
    try:
        f = float(s)
    except:
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f

def getLine():

    line = sys.stdin.readline()
    if not line:
        sys.stdout.write("\nCould not read a line from standard input. Goodbye\n")
        sys.exit(1)
    return line

    # try:
    #     line = sys.stdin.readline()
    # except:
    #     out("Goodbye")
    #     sys.exit(1)
    # if not line:
    #     sys.exit(1)
    # return line


def logRotation(R):
    out(f"Your rotation matrix is < {R} \n>")

def logSensorV(O):
    out(f"<+X-Axis:{O[0]}\n")
    out(f"+Y-Axis:{O[1]}\n")
    out(f"+Z-Axis:{O[2]}\n")
    out(f"-X-Axis:{O[3]}\n")
    out(f"-Y-Axis:{O[4]}\n")
    out(f"-Z-Axis:{O[5]}\n>")

@timeout(time)
def doChallenge():
    setup()
    out("First things first, what is the expected magnitude of measured voltage on the sun sensor?\n Assume the sun sensor has 10%% efficiency, is 1 AU from the sun, has an area of 1 cm, and a 10 ohm resistor as a voltmeter.\n")
    out("(Format answers as a single float): ")
    V0 = get_V0()
    while True: 
        line = getLine()
        log(f"{line}")
        Vguess = toFloat(line)
        if Vguess is None:
            out("Voltage should be a real number....\n")
            out("Try again: ")
            continue
        elif math.isclose(V0, Vguess, rel_tol=1e-3):
            out("Good, we're on the same page! Moving on...\n")
            break
        else:
            log(f"Should be: {V0}\n")
            out("Not quite, try again: ")

    
    out("Here are the initial voltages of the 6 sensors:\n")
    logSensorV(observed0())
    out("OK let's figure out what's wrong\n")
    out("Specify a rotation to apply to the satellite for the next measurements.\n")
    out("All units are in degrees\n")
    out("(Format answers as euler angles in the form \"r:X,Y',Z''\"):\n")
    out("Rotations are not cummulative, each rotation originates from the initial postion\n")
    out("You may also submit a rotation matrix directly\n")
    out("Format the rotation matrix as \"r:i11,i12,i13,i21,i22,i23,i31,i32,i33\"\n Where ijk represents element i in the jth row and the kth column.\n")
    out("At any point, you can submit your final answer in form: \"s:X,Y,Z\"\n")
    out("The final answer should be a unit vector\n")

    while True:
        line = getLine()
        log(f"{line}")
        try:
           cmd, vec = line.split(":")
        except:
            out("Invalid commmand format\n")
            continue
        if cmd == "s":
            log("Check: {vec}\n")
            break
        elif cmd == "r":
            # Apply rotation
            log(f"Rotation: {vec}\n")
            vec = vec.replace('\n','')
            angles = vec.split(',')
            try: 
                if len(angles) == 3:
                    phi, theta, psi = [toFloat(i) for i in angles]
                    R = Rotation(phi, theta, psi)
                elif len(angles) == 9:
                    R = np.matrix(np.array([toFloat(i) for i in angles]).reshape((3,3)))
                logRotation(R)
                logSensorV(observed1(R))
            except: 
                out("Invalid commmand format\n")
        else:
            out("Invalid commmand format\n")

    ## Check solution
    S = vec.replace('\n','')
    S = S.split(',')
    x, y, z = [toFloat(i) for i in S]
    tilt = Cart_Vector(x,y,z)
    if check_correct(tilt):
        
        out("Here is your flag!!")
        return True
    else:
        return False


def main():
    intro()
    try:
        if doChallenge():
            out(os.getenv("FLAG", "FLAG{foobar}!"))
            log("++Flag Sent")
        else:
            out("Nope, you got it wrong...!\n")
    except TimeoutError:
        sys.stdout.write("\nTimeout, Bye\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
