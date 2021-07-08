import os
import sys
import socket
from time import sleep
from datetime import datetime, timezone
import radar
from skyfield.api import wgs84


def send_hardcoded_orbital_parameters():

    inclination = str(radar_helper.INCLINATION) + '\n'
    s.send(inclination.encode('utf-8'))

    raan = str(radar_helper.RAAN) + '\n'
    s.send(raan.encode('utf-8'))

    eccentricity = str(radar_helper.ECCENTRICITY) + '\n'
    s.send(eccentricity.encode('utf-8'))

    aop = str(radar_helper.AOP) + '\n'
    s.send(aop.encode('utf-8'))

    mean_anomaly = str(radar_helper.MEAN_ANOMALY) + '\n'
    s.send(mean_anomaly.encode('utf-8'))

    mean_motion = str(radar_helper.MEAN_MOTION) + '\n'
    s.send(mean_motion.encode('utf-8'))


def send_orbital_parameters(i, ra, e, a, ma, mm):

    i = str(i) + '\n'
    s.send(i.encode('utf-8'))

    ra = str(ra) + '\n'
    s.send(ra.encode('utf-8'))

    e = str(e) + '\n'
    s.send(e.encode('utf-8'))

    a = str(a) + '\n'
    s.send(a.encode('utf-8'))

    ma = str(ma) + '\n'
    s.send(ma.encode('utf-8'))

    mm = str(mm) + '\n'
    s.send(mm.encode('utf-8'))


def solve():
    t = datetime.strptime('2021-06-27-00:09:52.000-UTC', '%Y-%m-%d-%H:%M:%S.%f-%Z')
    t.replace(tzinfo=timezone.utc)
    
    kwajalein = wgs84.latlon(8.7256, 167.715, 35)

    pulses = radar.parse_radar_data('radar_data.txt')

    orbit = radar.estimateOrbit(kwajalein,pulses)

    return orbit

if __name__ == "__main__":
    # get host from environment
    host = os.getenv("CHAL_HOST")
    if not host:
        print("No HOST supplied from environment")
        sys.exit(-1)

    # get port from environment
    port = int(os.getenv("CHAL_PORT", "0"))
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

    # receive challenge intro
    i = 0
    while i < 16:
        challenge = s.recv(64)
        challenge = challenge.decode('UTF-8')
        print(challenge,end='')
        i += 1
        sleep(0.1)

    challenge = s.recv(1024)
    challenge = challenge.decode('UTF-8')
    print(challenge,end='')

    sleep(2)

    
    # provide response
    a = solve()
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
    
