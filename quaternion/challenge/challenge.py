# Quaternion Challenge
import os, sys
from numpy import dot, cross, array
from numpy.linalg import norm
from time import sleep

from timeout import timeout, TimeoutError
time = int(os.getenv("TIMEOUT",90))

def render_intro(vec):
    art = [
        "            QUATERNION                 ",
        "            CHALLANGE                  ",
        "                                       ",
        "               z                       ",
        "               |                       ",
        "             __|____                   ",
        "            /  |   /|                  ",
        "  ______   /______/ |    ______        ",
        " |      |==|      | ====|      |---y   ",
        " |______|  |  /   | /   |______|       ",
        "           |_/____|/                   ",
        "            /                          ",
        "           /                    /x     ",
        "          x               z_ _ /       ",
        "        Satellite              \       ",
        "          Body                  \y     ",
        "         Frame             J2000       ",
        "                                       "
    ]
    # Challenge Intro
    for row in art:
        print(row)
        sleep(0.05)
        sys.stdout.flush()

    print("A spacecraft is considered \"pointing\" in the direction of its z-axis or [0,0,1] vector in the \"satellite body frame.\"")
    print("In the J2000 frame, the same spacecraft is pointing at ",vec[0],".",sep='')
    print("Determine the spacecraft attitude quaternion.")
    
    return


def quaternion(u,v):
    u = u / norm(u)
    v = v / norm(v)

    q = [0,0,0,0]
    q[0:3] = cross(u,v)
    q[3] = 1 + dot(u,v)
    q = q / norm(q)
    return q

@timeout(time)
def challenge():
    satBodyRef = [0,0,1]
    satDirVec = [1,-7,0.3]
    satDirVec = satDirVec/norm(satDirVec)
    
    render_intro([satDirVec])

    qA = quaternion(satBodyRef, satDirVec)
    
    #print(Qt)

    sys.stdout.flush()
    print("Qx = ",end='')
    x = input()

    print("Qy = ",end='')
    y = input()


    print("Qz = ",end='')
    z = input()

    
    print("Qw = ",end='')
    w = input()

    print()

    qB = [float(x), float(y), float(z), float(w)]

    qE = array(qB) - array(qA)

    for e in qE:
        if abs(e) > 0.001:
            return 0
    return 1

if __name__ == "__main__":
    # Challenge
    try:
        success = challenge()
    except TimeoutError:
        sys.stdout.write("\nTimeout, Bye\n")
        sys.exit(1)


    
    if success:
        print("You got it! Here's your flag:")
        flag = os.getenv('FLAG')
        print(flag)

    else:
        print("That didn't work, try again!")
