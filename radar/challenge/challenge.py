# Radar Challenge
import os, sys
import radar
from time import sleep
from datetime import datetime, timezone

from skyfield.api import load, wgs84

from timeout import timeout, TimeoutError

time = int(os.getenv("TIMEOUT", 180)) # Timeout after 180 seconds

ts = load.timescale()

def intro():
    art = [
        "                             RADAR                            ",
        "                           CHALLENGE                          ",
        "                                                              ",
        "                                                              ",
        "                      +o+                                     ",
        "                   o    .                                     ",
        "               o         .                                    ",
        "            o             .                                   ",
        "          o                .r                                 ",
        "        o                   .                                 ",
        "      o                      .                                ",
        "    o                         .                               ",
        "   o                           . az,el                        ",
        "  o                  ...........A......                       ",
        " o      .................          ............               ",
        "   .......                                    ...........     ",
        ".....                                                    .....",
    ]

    for row in art:
        print(row)
        sleep(0.05)
        sys.stdout.flush()

    print("\n")
    print("Welcome to the Radar Challenge!")
    print("Given the radar pulse returns of a satellite, determine its orbital parameters (assume two-body dynamics).")
    print("Each pulse has been provided as:")
    print("   t,  timestamp (UTC)")
    print("   az, azimuth (degrees) +/- 0.001 deg")
    print("   el, elevation (degrees) +/- 0.001 deg")
    print("   r,  range (km) +/- 0.1 km")
    print("The radar is located at Kwajalein, 8.7256 deg latitude, 167.715 deg longitude, 35m altitude.")
    print("\nEstimate the satellite's orbit by providing the following parameters:")
    print("   a,  semi-major axis (km)")
    print("   e,  eccentricity (dimensionless)")
    print("   i,  inclination (degrees)")
    print("   Ω,  RAAN (degrees)")
    print("   ω,  argument of perigee (degrees)")
    print("   υ,  true anomaly (degrees)")

    return

def getInput(t):

    sys.stdout.flush()

    print("\nWhat is the satellite's orbit at ",t," UTC?",sep='')
    try:
        a = float(input('   a (km):  '))
        e = float(input('   e:       '))
        i = float(input('   i (deg): '))
        Ω = float(input('   Ω (deg): '))
        ω = float(input('   ω (deg): '))
        υ = float(input('   υ (deg): '))
    except:
        print("Invalid input")
    
    answer = [a, e, i, Ω, ω, υ, t]

    return answer

@timeout(time)
def challenge():
    t = datetime.strptime('2021-06-27-00:09:52.000-UTC', '%Y-%m-%d-%H:%M:%S.%f-%Z')
    t.replace(tzinfo=timezone.utc)
    
    kwajalein = wgs84.latlon(8.7256, 167.715, 35)

    pulses = radar.parse_radar_data('radar_data.txt')

    #orbitA = radar.estimateOrbit(kwajalein,pulses)
    orbitA = [23000, 0.7, 34.0, 78.0, 270.0, 66.384, t]
    orbitB = getInput(t)

    # Compare answers to true orbit
    if abs(orbitA[0]-orbitB[0]) > 100:    return 0 # a (km)
    if abs(orbitA[1]-orbitB[1]) > 0.005:  return 0 # e (dimensionless)
    if abs(orbitA[2]-orbitB[2]) > 0.05:   return 0 # i (deg)
    if abs(orbitA[3]-orbitB[3]) > 0.05:   return 0 # Ω (deg)
    if abs(orbitA[4]-orbitB[4]) > 0.1:    return 0 # ω (deg)
    if abs(orbitA[5]-orbitB[5]) > 0.1:    return 0 # υ (deg)

    return 1

if __name__ == "__main__":
    # Challenge Intro
    intro()

    # Run Challenge
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
        print("\nNot close enough, try again.\n")