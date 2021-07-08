# Kepler Solver
import os, sys, socket
from numpy import dot, cross, sqrt
from numpy.linalg import norm
from time import sleep
from datetime import datetime, timezone

from kepler import pvt2kepler, prop, kepler2pvt

def solve(pvt0):
    μ = 3.986004418e5 #km^3/s^2

    # Get orbital elements
    orbit0 = pvt2kepler(pvt0)

    # Propagate until r = 42,164 km (GEO)
    dt = 0
    r = 0
    while r < 42164:
        orbit1 = prop(dt, orbit0)
        pvt1 = kepler2pvt(orbit1)
        r_ = pvt1[0:3]    
        r = norm(r_)
        dt = dt+1

    v_ = pvt1[3:6]
    t1 = pvt1[6]

    # Required velocity for GEO-stationary
    vGEO = sqrt(μ*(2/r - 1/(r)))
    vGEO_ = vGEO * cross([0,0,1],r_/r)

    deltaV = vGEO_ - v_

    t1 = t1.strftime('%Y-%m-%d-%H:%M:%S.%f-%Z')

    return t1, deltaV[0], deltaV[1], deltaV[2]

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

    # receive challenge
    i = 0
    while i < 22:
        challenge = s.recv(64)
        challenge = challenge.decode('UTF-8')
        print(challenge,end='')
        i += 1

    challenge = s.recv(256)
    challenge = challenge.decode('UTF-8')
    print(challenge,end='')

    sleep(2)
    t0 = datetime.strptime('2021-06-26-19:20:00.000-UTC', '%Y-%m-%d-%H:%M:%S.%f-%Z')
    t0 = t0.replace(tzinfo=timezone.utc)
    pvt0 = [8449.401305, 9125.794363, -17.461357, -1.419072, 6.780149, 0.002865, t0]

    a = solve(pvt0)
    
    
    i=0
    while i < len(a):
        response = str(a[i])+'\n'
        s.send(response.encode("utf-8"))
        print(response, end='')
        
        r = s.recv(256)
        print(r.decode('utf-8'),end='')
        i = i+1
        sleep(0.5)
    print()
    
