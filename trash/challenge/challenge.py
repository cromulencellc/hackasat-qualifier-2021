# Take Out The Trash Challenge

import os, sys

from skyfield.api import load
ts = load.timescale()

from numpy import arange, cross, dot
from numpy.linalg import norm

import os
from math import sqrt

from datetime import datetime

from timeout import timeout, TimeoutError

time = int(os.getenv("TIMEOUT", 60*3))

# Propagate orbits through time with steps of 60 seconds
lastFired = {}


def execCommand(cmd):
    t = ts.utc(2021,6,26,0,0,epSec(cmd[0]))
    print(t.utc_strftime(),": Executing Command ", cmd, sep='')
    satName = cmd[1]
    cmdsat = None

    # Check if laser fired less than 60 seconds ago
    if satName in lastFired:
        if (epSec(cmd[0]) - lastFired[satName]) < 60:
            print("Command failed, laser is cooling down!")
            return 0

    for sat in sats:
        if sat.name.upper() == satName:
            cmdSat = sat
    q = cmd[3:7]
    r = cmd[7]
    if r > 100:
        print(r, "km target range is too far!")
        return 0

    # Check if laser hits the space junk
    satPos = cmdSat.at(t).position.km
    u = [0,0,1]
    vCheck = u + 2*q[3]*cross(q[0:2],u) + 2*(cross(q[0:2],cross(q[0:2],u)))
    vCheck = vCheck*r + satPos

    lastFired[satName] = epSec(cmd[0])
    for junk in spacejunk:
        junkPos = junk.at(t).position.km
        rVec = vCheck - junkPos
        if norm(rVec) < 0.01: #if within 10m
            print(junk.name, " was destroyed by ", cmdSat.name, "!",sep='')
            spacejunk.remove(junk)
            return 1
    print(cmdSat.name, "fired and missed!")
    return 0

#Convert tCMD to EpSecs
#2021177.0545 -> 19980
def epSec(timeStr):
    a = datetime(2021,6,26,0,0,0)
    b = datetime.strptime(timeStr, '%Y%j.%H%M%S')

    epSec = (b-a).total_seconds()

    return epSec

#  quaterion from sat1 to sat2
def attitude2sat(sat1, sat2, t):
    sat1Pos = sat1.at(t).position.km #J2000 ICR
    sat2Pos = sat2.at(t).position.km #J2000 ICR
    v = [ \
        sat2Pos[0] - sat1Pos[0], \
        sat2Pos[1] - sat1Pos[1], \
        sat2Pos[2] - sat1Pos[2]]

    u = [0, 0, 1] # use z vector for pointing
    
    #print("v: ", v[0],v[1],v[2])
    v = v / norm(v) # normalize v

    # construct quaternion
    q = [0,0,0,0]
    q[0:3] = cross(u,v)
    q[3] = 1 + dot(u,v)
    q = q / norm(q) # normalize q

    #vCheck = u + 2*q[3]*cross(q[0:2],u) + 2*(cross(q[0:2],cross(q[0:2],u)))

    return q

# range from sat1 to sat2
def range2sat(sat1, sat2, t):
    sat1Pos = sat1.at(t).position.km #J2000 ICR
    sat2Pos = sat2.at(t).position.km #J2000 ICR
    r = sqrt( \
            (sat1Pos[0]-sat2Pos[0])**2 + \
            (sat1Pos[1]-sat2Pos[1])**2 + \
            (sat1Pos[2]-sat2Pos[2])**2)
    return r

# @timeout(time)
def simulate(cmds, sats, spacejunk):
    i=0
    tCMD = '2021177.0000'
    try:
        tCMD = (cmds[i][0])    
    except:
        print("No valid commands provided.")

    #Convert tCMD to EpSecs
    #2021177.0545 -> 19980
    tCMD = epSec(tCMD)

    while True:
        t = ts.utc(2021, 6, 26.00000000) # epoch from TLEs
        tVec = arange(0,3600*24,60) # 60 second time steps for 1 day
        for x in tVec:
            t = ts.utc(2021,6,26,0,0,x)
            # Check if a command is scheduled
            if x >= tCMD and i < len(cmds) and tCMD !=0:
                execCommand(cmds[i])
                i = i+1
                if i < len(cmds):
                    tCMD = epSec(cmds[i][0])
            print("Time: ",t.utc_strftime(),end='\r')
            for sat in sats:
                for junk in spacejunk:
                    r = range2sat(sat,junk,t)
                    # Check if less than 10km
                    if r<10:
                        print(t.utc_strftime(),": ",junk.name," conjuncted with ",sat.name,"!",sep='')
                        #print("Range: ", r, "km")
                        att = attitude2sat(sat, junk, t)
                        return 0
        if len(spacejunk) < 20:
            return 1

def enterCommands():
    cmdNum = 1
    commands = []
    while(True):
        print('CMD ',cmdNum,': ', end='', sep='')
        cmd = input()
        if cmd != '': commands.append(cmd)
        cmdNum = cmdNum+1
        if cmd == '':
            print("\r\rAll commands entered.")
            return commands

def buildCmdSequence(commandStrings):
    cmds = []
    for string in commandStrings:
        cmd = string.split()
        try:
            #cmd[0] = float(cmd[0])
            cmd[3] = float(cmd[3]) #q as float
            cmd[4] = float(cmd[4])
            cmd[5] = float(cmd[5])
            cmd[6] = float(cmd[6])
            cmd[7] = float(cmd[7]) #range as float
            cmds.append(cmd)    
        except:
            print("Command format not recognized: ", cmd)

    return cmds

@timeout(time)
def do_work(the_sats, the_spacejunk):

    # Request laser firing commands
    # [Time_UTC] [Sat_ID] [Fire] [Qx] [Qy] [Qz] [Qs] [Range_km]
    # "2021177.053300 SAT1 FIRE -0.7993071284697775 0.25691449215763607 0.0 0.5432338889435954 87.827103"
    # Quaternion rotates a [0,0,1] vector in the J2000 frame originating from the s/c position at time t
    print("Provide command sequences:")
    commands = enterCommands()

    # Parse commands into an array
    cmdSeq = buildCmdSequence(commands)
    print("\nStarting command sequence.")

    # # Propagate orbits through time with steps of 60 seconds
    # lastFired = {}

    success = simulate(cmdSeq, the_sats, the_spacejunk)

    return success

if __name__ == "__main__":
    # Challenge Intro
    print("A cloud of space junk is in your constellation's orbital plane.")
    print("Use the lasers on your satellites to vaporize it!")
    print("The lasers have a range of 100km. Don't allow any space junk to approach closer than 30km.")
    print("Use the provided TLEs for your spacecraft and the space junk. Provide commands in the following format:")
    print("[Time_UTC] [Sat_ID] FIRE [Qx] [Qy] [Qz] [Qw] [Range_km]\n")

    # TLEs provided via generator
    # Load Sats
    sats = load.tle_file('common/sats.tle')
    #print('Loaded',len(sats),'sats')
    # Load Space Junk
    spacejunk = load.tle_file('common/spacejunk.tle')
    #print('Loaded',len(spacejunk),'space junk\n')
    amtJunk = len(spacejunk)

    try:
        success = do_work(sats, spacejunk)
    except TimeoutError:
        sys.stdout.write("\nTimeout, Bye\n")
        sys.exit(1)

    if success:
        amtDestroyed = amtJunk - len(spacejunk)
        print(amtDestroyed, "pieces of space junk have been vaporized! Nice work!")
        flag = os.getenv('FLAG')
        print(flag)

    else:
        remaining = []
        for junk in spacejunk:
            remaining.append(junk.name)
        print("Space junk remaining:", remaining)
        print("\nThat didn't work, try again!")
