# Take Out The Trash Challenge

import os, sys

from skyfield.api import load, wgs84
ts = load.timescale()

from numpy import arange, cross, dot, matmul, array, arccos
from numpy.linalg import norm

import os, pytz
from math import pi, sin, cos

from datetime import datetime, timedelta

from timeout import timeout, TimeoutError

time = int(os.getenv("TIMEOUT", 60*3))


class GroundStation:
    def __init__(self,name,pos):
        self.name = name
        self.pos = pos


def propQuaternion(q0,dt):
    w0 = [0.1*pi/180, 0.1*pi/180, 0.1*pi/180] #rad/s
    w = [w0[0]*dt, w0[1]*dt, w0[2]*dt]
    nw = norm(w)
    if nw == 0:
        return q0
    qw = [w[0]/nw*sin(nw/2), w[1]/nw*sin(nw/2), w[2]/nw*sin(nw/2), cos(nw/2)]

    q1 = multiplyQuaternion(qw,q0)
    q1 = q1 / norm(q1)
    return q1

def multiplyQuaternion(q0,q1):
    x0, y0, z0, w0 = q0
    x1, y1, z1, w1 = q1
    return array([x1 * w0 + y1 * z0 - z1 * y0 + w1 * x0,
                     -x1 * z0 + y1 * w0 + z1 * x0 + w1 * y0,
                     x1 * y0 - y1 * x0 + z1 * w0 + w1 * z0,
                     -x1 * x0 - y1 * y0 - z1 * z0 + w1 * w0,])

# [qx,qy,qz,qw]
def quaternion(u,v):
    u = u / norm(u)
    v = v / norm(v)

    q = [0,0,0,0]
    q[0:3] = cross(u,v)
    q[3] = 1 + dot(u,v)
    q = q / norm(q)
    return q

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
        # 'TIME_UTC GND_STATION CMD SPINNY CMD_WORD'
        cmd = string.split()
        try:
            assert len(cmd) == 5, print('Number of command parameters mismatched')
            # 2021-06-26 00:00:00 UTC
            try:
                cmd[0] = datetime.strptime(cmd[0], '%Y-%m-%d-%H:%M:%S-%Z')
                cmd[0] = cmd[0].replace(tzinfo=pytz.utc)
            except:
                print("Invalid time format")
            assert cmd[1] in validGroundStations, print('Not a valid ground station')
            assert cmd[2] == 'CMD'
            assert cmd[3] == 'SPINNY'
            assert cmd[4] in validCommandWords, print('Not a valid command word')
            cmds.append(cmd)    
        except:
            print("Command format not recognized:", string)
            print("Command format example:        2021-06-26-01:00:00-UTC BANGALOR CMD SPINNY PLEASE")

    return cmds

def checkAccess(t,satPos,attitude,gndPos):
    q = attitude
    u = [0,0,1]
    a = u + 2*q[3]*cross(q[0:2],u) + 2*(cross(q[0:2],cross(q[0:2],u)))
    b = gndPos - satPos
    ang = arccos(dot(a,b)/(norm(a)*norm(b))) * 180/pi
    # comms can be established if pointed within 45 degrees
    if ang < 45:
        return 1
    return 0



def uplinkCommand(t, cmd, sat, q0, q1, gndStns):
    print("Time:",t.utc_strftime(),"Executing Command",cmd[1:5])
    station = None
    for stn in gndStns:
        if stn.name == cmd[1]:
            station = stn

    print(station.name,": establishing uplink with SPINNY...",sep='')
    satPos = sat.at(t).position.km
    gndPos = station.pos.at(t).position.km
    if checkAccess(t,satPos,q0,gndPos):
        print(station.name,": uplink established!",sep='')
        dt = t.utc_datetime()
        dt2 = dt + timedelta(seconds=180)
        t2 = ts.from_datetime(dt2)
        satPos = sat.at(t2).position.km
        gndPos = station.pos.at(t2).position.km
        if checkAccess(t2,satPos,q1,gndPos):
            print("SPINNY: RECEIVED COMMAND \'",cmd[4],'\' AT ',t2.utc_strftime(),sep='')
            return cmd[4]
        print(station.name,": uplink lost before transmission completed. Command \'",cmd[4],"\' was not sent.",sep='')
        return 0
    print(station.name,": uplink could not be establised! Command \'",cmd[4],"\' was not sent.",sep='')
    return 0


def simulate(tArray,sat,gnd,cmds): 
    #antRef = [0,0,1] # antenna aligned with satellite Z axis 
    satRef = [0,0,1] # use satellite Z axis for reference
    satDir = [1,0,0] # initial satellite direction in J2000 frame
    satAtt0 = quaternion(satRef, satDir) # initial attitude quaternion

    # Satellite spin rates
    #satAttDot = quaternionDot(satAtt0, sat_wx, sat_wy, sat_wz)
    #print("qDot:", satAttDot)

    receivedCommands = ''

    epoch = tArray[0].utc_datetime()
    tStep = (tArray[1].utc_datetime() - tArray[0].utc_datetime()).total_seconds()
    tCmd = 0
    if cmds:
        cmd = cmds[0]
        tCmd = (cmd[0] - epoch).total_seconds()
    iCmd = 0
    
    i = 0
    #list = [0,1,30,60,3600]
    for t in tArray:
        epSec = tStep * i
        # Execute commands at correct time
        if tCmd and epSec == tCmd and iCmd < len(cmds):
            satAtt = propQuaternion(satAtt0,tStep*i)
            satAtt2 = propQuaternion(satAtt0,tStep*i+180)
            upCmd = uplinkCommand(t, cmd, sat, satAtt, satAtt2, gnd)
            if upCmd:
                if receivedCommands != '':
                    receivedCommands += ' '
                receivedCommands += upCmd
            iCmd += 1
            if iCmd < len(cmds):
                cmd = cmds[iCmd]
                tCmd = (cmd[0] - epoch).total_seconds()

        print("Time:",t.utc_strftime(),end='\r')
        
        # Propagate
        i += 1

    print("\nSPINNY received:",receivedCommands)
    if receivedCommands == 'PLEASE STOP SPINNING!':
        return 1
    return 0


@timeout(time)
def do_work(the_spinny, the_ground_stations):
    # Provide Uplink Sequence
    # 'TIME_UTC GND_STATION CMD SPINNY CMD_WORD'
    print("\nEnter commands")
    commands = enterCommands()
    commandSequence = buildCmdSequence(commands)

    # Start simulation
    tArray  = ts.utc(2021, 6, 26, 0, 0, range(60*60*12))
    success = simulate(tArray, the_spinny, the_ground_stations, commandSequence)
    return success


if __name__ == "__main__":
    # Challenge Intro
    print("We've lost control of our spacecraft, Spinny, and it is now tumbling in orbit!")
    print("Spinny uses a directional antenna for command and control so we will have to uplink the rescue commands at just the right times from ground stations around the globe.")
    print("The spacecrafy body spin rates are a constant [0.1, 0.1, 0,1] rad/s in XYZ axes")
    print("The initial antenna direction is [1,0,0] in the J2000 frame at 2021-06-26 00:00:00 UTC.")
    print("The antenna will receieve if pointed within 45 degrees of a ground station")

    # Load Spinny's TLE
    sats = load.tle_file('spinny.tle')
    spinny = sats[0]
    if spinny: print("Loaded Spinny's TLE")
    
    # Load ground stations
    bangalor = GroundStation('BANGALOR',wgs84.latlon(13.0344, 77.5116, 823)) # geodetic, WGS-84
    grimstad = GroundStation('GRIMSTAD',wgs84.latlon(58.33, 8.35, 211))
    svalbard = GroundStation('SVALBARD',wgs84.latlon(78.2307, 15.3897, 497))
    trollsat = GroundStation('TROLLSAT',wgs84.latlon(-72.0117, 2.53838, 1400))
    tromso   = GroundStation('TROMSO',wgs84.latlon(69.6625, 18.9408, 134))

    groundStations = [bangalor, grimstad, svalbard, trollsat, tromso]
    validGroundStations = ['BANGALOR', 'GRIMSTAD', 'SVALBARD', 'TROLLSAT', 'TROMSO']
    validCommandWords = ['PLEASE', 'STOP', 'SPINNING!']
    print("Loaded",len(groundStations),"ground stations")

    # # Provide Uplink Sequence
    # # 'TIME_UTC GND_STATION CMD SPINNY CMD_WORD'
    # print("\nEnter commands")
    # commands = enterCommands()
    # commandSequence = buildCmdSequence(commands)
    #
    # # Start simulation
    # tArray  = ts.utc(2021, 6, 26, 0, 0, range(60*60*12))
    # success = simulate(tArray, spinny, groundStations, commandSequence)

    try:
        success = do_work(spinny, groundStations)
    except TimeoutError:
        sys.stdout.write("\nTimeout, Bye\n")
        sys.exit(1)

    if success:
        print("You saved Spinny! Nice work!")
        flag = os.getenv('FLAG')
        print(flag)

    else:
        print("\nSpinny is still spinning, try again!")
