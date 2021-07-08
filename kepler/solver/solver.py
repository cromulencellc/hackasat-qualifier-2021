# Kepler Solver
import os, sys, socket
from numpy import dot, cross, array
from numpy.linalg import norm
from time import sleep

from kepler import pvt2kepler

def solve(pvt):
    #[a, e, i, Ω, ω, υ] = [24732.886033, 0.706807, 0.118, 90.227, 226.587, 90.390]
    [a, e, i, Ω, ω, υ] = pvt2kepler(pvt)
    elements = [a, e, i, Ω, ω, υ]
    return elements

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
        sleep(1)
        prompt = s.recv(128)  # "Ticket please:"
        s.send((ticket + "\n").encode("utf-8"))

    # receive challenge
    i = 0
    while i < 17:
        challenge = s.recv(64)
        challenge = challenge.decode('UTF-8')
        print(challenge,end='')
        i += 1

    challenge = s.recv(1024)
    challenge = challenge.decode('UTF-8')
    print(challenge,end='')

    sleep(2)

    pvt = [8449.401305, 9125.794363, -17.461357, -1.419072, 6.780149, 0.002865, '2021-06-26-19:20:00.000-UTC']

    a = solve(pvt)

    i=0
    while i < len(a):
        response = str(a[i])+'\n'
        s.send(response.encode("utf-8"))
        print(response, end='')
        
        r = s.recv(256)
        print(r.decode('utf-8'),end='')
        i = i+1
        sleep(0.5)
    r = s.recv(256)
    print()
