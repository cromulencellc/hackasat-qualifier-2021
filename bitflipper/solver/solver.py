# BitFlipper Solver 
import os
import sys
import socket
import time

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
        prompt = s.recv(64)  # "Ticket please:"
        s.send((ticket + "\n").encode("utf-8"))


    # receive challenge
    i = 0
    while i < 23:
        challenge = s.recv(128)
        challenge = challenge.decode('UTF-8')
        print(challenge,end='')
        i += 1

    responses = [
        '161','4',
        '161','5',
        '161','7'
    ]
    

    # provide commands
    for resp in responses:
        response = resp + "\n"
        print(resp)
        s.send(response.encode("utf-8"))
        r = s.recv(64)
        print(r.decode('utf-8'),end='')
        time.sleep(1)
    response = "\n\n"
    print(response)
    s.send(response.encode("utf-8"))

    time.sleep(2)

    # receive the rest of the challenge response
    i = 0
    while (i <10000):
        r = s.recv(32)
        print(r.decode('utf-8'),end='')
        i = i+1

    