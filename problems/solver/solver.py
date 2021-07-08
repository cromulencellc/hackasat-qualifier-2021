from pwn import p32, p64, u32, u64, context, remote
import os, sys
import numpy as np
import math as m
import re

def out(s:str):
    sys.stdout.write(s)
    sys.stdout.flush()

def get_V0():
    Lsol = 3.83e26 #W joules/cm^2/s
    R = 10 #ohm
    A = 1 #cm^2
    e = .10
    AU = 1.496e13 #cm

    P = e*Lsol*A**2/(4*m.pi*AU**2)
    V0 = np.sqrt(P*R)
    return V0

def parse_obs(obs):

    o = re.findall( r'\d+\.*\d*', obs.decode("utf-8"))
    return np.array(list(map(float, o)))

def parse_R(R):
    r = re.findall( r"[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", R.decode("utf-8"))
    r = np.array(list(map(float, r)))
    r = np.reshape(r, (3,3))
    return r

def mag(o):
    mag = np.sqrt(np.sum(o**2))
    return mag 

def Error(obs,exp):
    E = np.abs((obs-exp)/exp)
    return E

def vec3(o):
    v = np.zeros(3)
    for i in range(len(v)):
        if o[i] != 0:
            v[i] = o[i]
        else:
            v[i] = -1*o[i+3]

    return v.reshape((3,1))

def rcv_obs():
    #print(p.can_recv(timeout = 10))
    p.recvuntil(b'<', drop=True, timeout=100)
    obs = p.recvuntil(b'>', timeout=10)
    o = parse_obs(obs)
    return o

def check_error(o, V0):
    Vmag = mag(o)
    E = Error(Vmag, V0)
    return (Vmag, E)

def id_sensor(o, o0):
    oo=o>0
    oo0=o0>0
    bad_sensor = np.arange(6)[oo^oo0]
    bad_sensor = bad_sensor[oo0[bad_sensor]]
    if len(bad_sensor)==0:
        bad_sensor = np.arange(6)[oo^oo0]
        return bad_sensor-3
    elif len(bad_sensor) > 1:
        return None
    elif oo0[bad_sensor]:
        return bad_sensor
    else: 
        return None
        

if __name__ == "__main__":
    p = remote(os.getenv("CHAL_HOST", "127.0.0.1"), os.getenv("CHAL_PORT", "19020"))
    
    # get ticket from environment
    ticket = os.getenv("TICKET")

    # pass ticket to ticket-taker
    if ticket:
        prompt = p.recv(128)  # "Ticket please:"
        p.send((ticket + "\n").encode("utf-8"))
        print("Sent Ticket")

    
    p.recvuntil(b':', drop=True)
    V0 = get_V0()
    print("V0:",V0)
    p.send(f"{V0}\n")
    #print(p.recvall())
    o0 = rcv_obs()
    Vmag0, E = check_error(o0, V0)
    out(f"The initial Voltage magnitude is {Vmag0}, Error {E}\n")
    
    i=0
    angle = [90, 0, 0, 90, 0]
    bad_sensor=None
    while (E > 0.005)  :
        out("One of the sensors must be tilted, rotating\n")
        p.send(f"r:{angle[i]},{angle[i+1]},{angle[i+2]}\n")
        print(f"r:{angle[i]},{angle[i+1]},{angle[i+2]}\n")
        p.recvuntil(b'<', drop=True)
        R = p.recvuntil(b'>', timeout=10)
        o = rcv_obs()
        print("2nd obs, ",  o)
        bad_sensor = id_sensor(o, o0)
        o[bad_sensor]= 0    
        Vmag, E = check_error(o, V0)
        out(f"{Vmag}, {E}, {bad_sensor}\n")
        if bad_sensor == None:
            E=1
        i+=1

    out(f"New Observed Vmag, {Vmag}, Error, {E}\n")
    R = parse_R(R)
    out(f"The rotation matrix you used is {R}\n")
    RT = R.transpose()
    oo = vec3(o)
    SunV = np.matmul(RT,oo)
    out(f"The correct Sun Vector should have been {SunV}\n")
    out(f"The tilted sensor id is {bad_sensor}\n")

    tilt = np.zeros(3)
    unit_SunV=SunV/mag(SunV)
    for i in np.arange(3):
        axis = np.zeros(3).reshape((3,1))
        axis[i] = [1]
        Rxsun = axis*unit_SunV.T
        Rxsun = Rxsun.flatten()
        strR = ",".join([str(element) for element in Rxsun.flatten()])
        p.send(f"r:{strR}\n")
        print(f"r:{strR}\n")
        p.recvuntil(b">", drop=True)
        o = rcv_obs()
        l = np.count_nonzero(o)
        if not (m.isclose(mag(o), V0, rel_tol=1e-3)):
            t = np.arccos(o[bad_sensor]/V0)
            tilt[i] = (np.cos(t))
        elif (l >0):

            t = np.arccos(o[bad_sensor]/V0)
            tilt[i] = (np.cos(t))
        else:
            axis[i] = [-1]
            Rxsun = axis*unit_SunV.T
            Rxsun = Rxsun.flatten()
            strR = ",".join([str(element) for element in Rxsun.flatten()])
            p.send(f"r:{strR}\n")
            print((f"r:{strR}\n"))
            p.recvuntil(b">", drop=True)
            o = rcv_obs()
            t = np.arccos(o[bad_sensor]/V0)
            tilt[i] = (-1*np.cos(t))
        
    
    p.send(f"s:{tilt[0]},{tilt[1]},{tilt[2]}\n")
    print(f"s:{tilt[0]},{tilt[1]},{tilt[2]}\n")
    #out(p.recvuntil(b'!!', drop = True))
    Flag = p.recvall()
    out(Flag.decode("utf-8"))
