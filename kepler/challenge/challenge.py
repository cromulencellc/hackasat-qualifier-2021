# Kepler Challenge
import os, sys
from numpy import dot, cross, array
from numpy.linalg import norm
from time import sleep

from kepler import pvt2kepler

from timeout import timeout, TimeoutError
time = int(os.getenv("TIMEOUT",60*3))

def render_intro(vec):
    art = [
        "         KEPLER        ",
        "        CHALLANGE      ",
        "       a e i Ω ω υ     ",
        "            .  .       ",
        "        ,'   ,=,  .    ",
        "      ,    /     \  .  ",
        "     .    |       | .  ",
        "    .      \     / .   ",
        "    +        '='  .    ",
        "     .          .'     ",
        "      .     . '        ",
        "         '             "
    ]
    # Challenge Intro
    for row in art:
        print(row)
        sleep(0.05)
        sys.stdout.flush()

    sleep(1)

    print("Your spacecraft reports that its Cartesian ICRF position (km) and velocity (km/s) are:")
    print("Pos (km):  ",vec[0:3])
    print("Vel (km/s):",vec[3:6])
    print("Time:      ",vec[6])
    print("\nWhat is its orbit (expressed as Keplerian elements a, e, i, Ω, ω, and υ)?")
    sys.stdout.flush()
    
    return

def getInput():
    
    print("Semimajor axis, a (km): ",end='')
    a = float(input())

    print("Eccentricity, e: ",end='')
    e = float(input())

    print("Inclination, i (deg): ",end='')
    i = float(input())

    print("Right ascension of the ascending node, Ω (deg): ",end='')
    Ω = float(input())

    print("Argument of perigee, ω (deg): ",end='')
    ω = float(input())

    print("True anomaly, υ (deg): ",end='')
    υ = float(input())

    return [a, e, i, Ω, ω, υ]

def solve(pvt):
    
    elements = pvt2kepler(pvt)

    # [a(km) e i(deg) Ω(deg) ω(deg) υ(deg)]
    #elements = [24732.886033, 0.706807, 0.118, 90.227, 226.587, 90.390]
    return elements

@timeout(time)
def challenge():
    
    pvt = [8449.401305, 9125.794363, -17.461357, -1.419072, 6.780149, 0.002865, '2021-06-26-19:20:00.000-UTC']
    
    render_intro(pvt)

    orbElemA = solve(pvt)
    orbElemB = getInput()

    i = 0
    while i < len(orbElemA):
        e = abs((orbElemB[i]-orbElemA[i])/orbElemA[i])
        if e > 0.1:
            return 0
        i = i+1
    
    return 1

if __name__ == "__main__":
    # Challenge
    try:
        success = challenge()
    except TimeoutError:
        sys.stdout.write("\nTimeout, Bye\n")
        sys.exit(1)

    if success:
        print("\nYou got it! Here's your flag:")
        flag = os.getenv('FLAG')
        print(flag)

    else:
        print("\nThat didn't work, try again!")
