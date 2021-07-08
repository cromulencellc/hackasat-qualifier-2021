# Hello World Solver
import os, sys, socket
from numpy import dot, cross, array
from numpy.linalg import norm
from time import sleep

def quaternion(u,v):
    u = u / norm(u)
    v = v / norm(v)

    q = [0,0,0,0]
    q[0:3] = cross(u,v)
    q[3] = 1 + dot(u,v)
    q = q / norm(q)
    return q

def solve():
    satBodyRef = [0,0,1]
    satDirVec = [0.14129425, -0.98905974,  0.04238827]

    q = quaternion(satBodyRef, satDirVec)
    
    return q

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
    while i < 21:
        challenge = s.recv(64)
        challenge = challenge.decode('UTF-8')
        print(challenge,end='')
        i += 1

    challenge = s.recv(256)
    challenge = challenge.decode('UTF-8')
    print(challenge,end='')

    sleep(1)

    Q = solve()

    # provide response
    Q = [0.68500346, 0.09785764, 0, 0.72193777]
    #Q[1] = 0.097
    i=0
    while i < 4:
        response = str(Q[i])+'\n'
        s.send(response.encode("utf-8"))
        print(response, end='')
        
        r = s.recv(256)
        print(r.decode('utf-8'),end='')
        i = i+1
        sleep(0.5)
    print()