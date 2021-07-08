# IQ Solver
import os
import sys
import socket

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
    challenge = s.recv(1028)
    challenge = challenge.decode('UTF-8')
    print(challenge,end='')

    # provide response
    iq = '-1.0 1.0 -1.0 -1.0 -1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 1.0 -1.0 -1.0 1.0 -1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 -1.0 1.0 1.0 1.0 -1.0 1.0 -1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 -1.0 -1.0 -1.0 1.0 1.0 -1.0 -1.0 1.0 -1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 1.0 -1.0 -1.0 1.0 1.0 1.0 -1.0 1.0 -1.0 -1.0 -1.0 -1.0 -1.0 -1.0 1.0 -1.0 1.0 -1.0'
    response = iq+'\n'
    print(response)
    s.send(response.encode("utf-8"))
    
    # receive and print flag
    i = 0
    while (i <4):
        r = s.recv(256)
        print(r.decode('utf-8'),end='')
        i = i+1
