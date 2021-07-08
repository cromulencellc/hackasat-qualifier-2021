# Conjunction Junction Solver 
import os
import sys
import socket
import re

from skyfield.api import load
ts = load.timescale()

from numpy import arange, cross, dot
from numpy.linalg import norm
from math import sqrt

from datetime import datetime

# Convert '2021-06-26 05:33:00 UTC' to '2021177.053300'
def cmdTime(timeStr):
    timeStr = timeStr.replace(" UTC", "")
    dt = datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S')
    tt = dt.strftime("%Y%j.%H%M%S")
    return tt

# range from sat1 to sat2
def range2sat(sat1, sat2, t):
    sat1Pos = sat1.at(t).position.km #J2000 ICR
    sat2Pos = sat2.at(t).position.km #J2000 ICR
    r = sqrt( \
            (sat1Pos[0]-sat2Pos[0])**2 + \
            (sat1Pos[1]-sat2Pos[1])**2 + \
            (sat1Pos[2]-sat2Pos[2])**2)
    return r

#  quaterion from sat1 to sat2
def attitude2sat(sat1, sat2, t):
    sat1Pos = sat1.at(t).position.km #J2000 ICR
    sat2Pos = sat2.at(t).position.km #J2000 ICR
    v = [ \
        sat2Pos[0] - sat1Pos[0], \
        sat2Pos[1] - sat1Pos[1], \
        sat2Pos[2] - sat1Pos[2]]

    u = [0, 0, 1] # use z vector for pointing
    
    v = v / norm(v) # normalize v

    # construct quaternion
    q = [0,0,0,0]
    q[0:3] = cross(u,v)
    q[3] = 1 + dot(u,v)
    q = q / norm(q) # normalize q
    
    return q

def calculateCommands():
    commands = []
    i=0
    lastFired = {}
    while True:
        t = ts.utc(2021, 6, 26.00000000) # epoch from TLEs
        tVec = arange(0,3600*24,60) # 60 second time steps for 1 day
        for x in tVec:
            t = ts.utc(2021,6,26,0,0,x)
            print("Time: ",t.utc_strftime(),end='\r')
            for sat in sats:
                for junk in spacejunk:
                    r = range2sat(sat,junk,t)
                    # Check if less than 90km
                    if r<90:
                        if sat.name not in lastFired:
                            lastFired[sat.name] = -100
                        if (x - lastFired[sat.name]) >= 60:
                            lastFired[sat.name] = x
                            print(t.utc_strftime(),": ",sat.name," targeting ",junk.name,"!",sep='')
                            tCmd = cmdTime(t.utc_strftime())
                            #print("Range: ", r, "km")
                            att = attitude2sat(sat, junk, t)
                            qStr = ''
                            for x in att:
                                qStr = qStr + str(x) + " "
                            cmd = tCmd + " " + sat.name.upper() + " FIRE " + qStr + str(r)
                            commands.append(cmd)
                            spacejunk.remove(junk)
            if x == tVec[len(tVec)-1]:
                print("Not all space junk could be targeted:", spacejunk)
                return commands
        if len(spacejunk) == 0:
            print(commands)
            return commands


if __name__ == "__main__":
    # get host from environment
    host = os.getenv("CHAL_HOST")
    if not host:
        print("No HOST supplied from environment")
        sys.exit(-1)

    # get port from environment
    port = int(os.getenv("CHAL_PORT","0"))
    if port == 0:
        print("No PORT supplied from environment")
        sys.exit(-1)

    # get ticket from environment
    ticket = os.getenv("TICKET")

    # connect to service
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
   
    # pass ticket to ticket-taker
    if ticket:
        prompt = s.recv(128)  # "Ticket please:"
        s.send((ticket + "\n").encode("utf-8"))

    print("\nVVVVVVVVVVVVVVVVVVVVVVV   SOLVER: Calculating commands VVVVVVVVVVVVVVVVVVVVVVV")
    # Load TLEs
    sats = load.tle_file('common/sats.tle')
    print('Loaded',len(sats),'sats')
    # Load Space Junk
    spacejunk = load.tle_file('common/spacejunk.tle')
    print('Loaded',len(spacejunk),'space junk\n')

    # calculate commands
    print("Calculating commands...")
    commands = calculateCommands()


    # receive math challenge
    challenge = s.recv(512)
    challenge = challenge.decode('UTF-8')
    print("\nVVVVVVVVVVVVVVVVVVVVVVV   SOLVER: Receiving challenge VVVVVVVVVVVVVVVVVVVVVVV")
    print(challenge)

    # provide commands
    for cmd in commands:
        response = cmd + "\n"
        print(cmd)
        s.send(response.encode("utf-8"))
        challenge = s.recv(256)
        challenge = challenge.decode('UTF-8')
        print(challenge,end='')
    
    response = "\n"
    s.send(response.encode("utf-8"))

    # receive the rest of the challenge response
    i = 0
    while (i <1028):
        r = s.recv(128)
        print(r.decode('utf-8'),end='')
        i = i+1

"""
    # get flag
    print("Testing recv(256)...")
    result = s.recv(256)
    print(result.decode("utf-8"))
"""