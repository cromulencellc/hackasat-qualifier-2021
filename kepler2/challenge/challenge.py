# Kepler Challenge
import os, sys
from numpy import cross, pi, sqrt
from numpy.linalg import norm
from time import sleep
from datetime import datetime, timezone

from kepler import pvt2kepler, prop, kepler2pvt

from timeout import timeout, TimeoutError
time = int(os.getenv("TIMEOUT",60*3))

def render_intro(vec):
    art = [
        "        KEPLER 2 GEO    ",
        "           t, Δv             ",
        "         CHALLANGE          ",
        "          .  .   .         ",
        "       .            .      ",
        "     .      .  .      .    ",
        "    .   ,'   ,=,  .    .   ",
        "   .  ,    /     \  .   .  ",
        "   . .    |       | .   .  ",
        "   ..      \     / .    .  ",
        "   ..        '='  .    .   ",
        "    .          .'     .    ",
        "     Δ . .  '       .      ",
        "       '  .  .   .         "
    ]
    # Challenge Intro
    for row in art:
        print(row)
        sleep(0.05)
        sys.stdout.flush()

    sleep(1)

    print("Your spacecraft from the first Kepler challenge is in a GEO transfer orbit.")
    print("Determine the maneuver (time and Δv vector) required to put the spacecraft into GEO-strationary orbit: a=42164+/-10km, e<0.001, i<1deg.")
    print("Assume two-body orbit dynamics and an instantaneous Δv in ICRF coordinates.")
    print("Pos (km):  ",vec[0:3])
    print("Vel (km/s):",vec[3:6])
    print("Time:      ",vec[6].strftime('%Y-%m-%d-%H:%M:%S.%f-%Z'))
    print("\nWhat maneuver is required?")
    sys.stdout.flush()
    
    return

def getInput(t0):
    print("Enter maneuver time in UTC following the example format.")
    print("Time: 2021-06-26-00:00:00.000-UTC",end='\r')
    t = input("Time: ")
    t = datetime.strptime(t, '%Y-%m-%d-%H:%M:%S.%f-%Z')
    t = t.replace(tzinfo=timezone.utc)
    dt = (t-t0).total_seconds()
    assert dt > 0 and dt < 60*60*12, "Time must be within 12 hours after %s" % t0

    print("Δv_x (km/s): ",end='')
    vx = float(input())

    print("Δv_y (km/s): ",end='')
    vy = float(input())

    print("Δv_z (km/s): ",end='')
    vz = float(input())
    
    deltaV = [vx,vy,vz]

    return t, deltaV

def maneuver(orbit0, deltaV):
    t0 = orbit0[6]
    t1 = deltaV[0]
    dt = (t1-t0).total_seconds()

    orbit0 = prop(dt, orbit0)
    pvt1 = kepler2pvt(orbit0)

    pvt1[3] = pvt1[3] + deltaV[1][0]
    pvt1[4] = pvt1[4] + deltaV[1][1]
    pvt1[5] = pvt1[5] + deltaV[1][2]

    orbit1 = pvt2kepler(pvt1)
    return orbit1

@timeout(time)
def challenge():
    t0 = datetime.strptime('2021-06-26-19:20:00.000-UTC', '%Y-%m-%d-%H:%M:%S.%f-%Z')
    t0 = t0.replace(tzinfo=timezone.utc)
    
    pvt0 = [8449.401305, 9125.794363, -17.461357, -1.419072, 6.780149, 0.002865, t0] # GTO
    
    render_intro(pvt0)
    
    # Calculate new orbit based on the provided maneuver
    orbit0 = pvt2kepler(pvt0)
    
    maneuverInput = getInput(t0)

    [a, e, i, Ω, ω, υ, t1] = maneuver(orbit0, maneuverInput)

    # Check if the new orbit meets the GEO-stationary requirements
    # a=42164+/-10km, e<0.001, i<1deg

    print("\nNew Orbit (a, e, i, Ω, ω, υ, t):\n", a, e, i*180/pi, Ω*180/pi, ω*180/pi, υ*180/pi, t1)
    if not abs(42164-a)<=10:
        print("Semi-major axis did not meet requirement: a=42164+/-10km")
        return 0
    if not e<0.001:
        print("Eccentricity did not meet requirement: e<0.001")
        return 0
    if not i<1:
        print("Inclination did not meet requirement: i<1deg")
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
        print("\nYou got it! Here's your flag:")
        flag = os.getenv('FLAG')
        print(flag)

    else:
        print("\nThat didn't work, try again!")
