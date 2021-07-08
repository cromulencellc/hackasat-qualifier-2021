# IQ Challenge
import os
from time import sleep
import sys

from timeout import timeout, TimeoutError
time = int(os.getenv("TIMEOUT", 90))

def render_intro(bitString):
    constellation = [
        "   QPSK Modulation   ",
        "          Q",
        "          |          ",
        "    01    |     11   ",
        "    o     |+1   o    ",
        "          |          ",
        "          |          ",
        "    -1    |     +1   ",
        "===================== I",
        "          |          ",
        "          |          ",
        "    00    |     10   ",
        "    o     |-1   o    ",
        "          |          ",
        "          |          ",
    ]
    # Challenge Intro
    print("IQ Challenge")
    for row in constellation:
        print(row)
        sleep(0.05)

    print("Convert the provided series of transmit bits into QPSK I/Q samples")
    print(
        "                  |Start here\n"
        "                  v\n",
        "Bits to transmit: ",bitString,sep='')
    print("Provide as interleaved I/Q e.g. 1.0 -1.0 -1.0  1.0 ... ")
    print("                                 I    Q    I    Q  ...")

def qpsk(bits):
    bits = bits.replace(' ','')
    iq = [0] * len(bits)
    i = 0
    while i < len(bits):
        bb = bits[i:i+2]
        if bb == '11':
            iq[i] = 1.0
            iq[i+1] = 1.0
        elif bb == '01':
            iq[i] = -1.0
            iq[i+1] = 1.0
        elif bb == '10':
            iq[i] = 1.0
            iq[i+1] = -1.0
        elif bb == '00':
            iq[i] = -1.0
            iq[i+1] = -1.0
        i += 2
    return iq

def checkResponse(bits, resp):
    respSamples = resp.split(' ')
    corrSamples = qpsk(bits)

    if len(respSamples) != len(corrSamples):
        print("Incorrect number of samples! Hint: there should be",len(corrSamples))
        return 0
    
    i = 0
    while i < len(corrSamples):
        if float(respSamples[i]) != corrSamples[i]:
            print("Incorrect I/Q sample found")
            return 0
        i += 1

    # -1.0 1.0 -1.0 -1.0 -1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 1.0 -1.0 -1.0 1.0 -1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 -1.0 1.0 1.0 1.0 -1.0 1.0 -1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 -1.0 -1.0 -1.0 1.0 1.0 -1.0 -1.0 1.0 -1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 1.0 -1.0 -1.0 1.0 1.0 1.0 -1.0 1.0 -1.0 -1.0 -1.0 -1.0 -1.0 -1.0 1.0 -1.0 1.0 -1.0


    return 1


@timeout(time)
def challenge():
    bitString = "01000011 01110010 01101111 01101101 01110101 01101100 01100101 01101110 01110100 00001010"
    
    render_intro(bitString)

    response = input('Input samples: ')

    if checkResponse(bitString, response):
        return 1
    return 0


if __name__ == "__main__":
    # Challenge
    try:
        success = challenge()
    except TimeoutError:
        sys.stdout.write("\nTimeout, Bye\n")
        sys.exit(1)

    if success:
        print("You got it! Here's your flag:")
        flag = os.getenv('FLAG')
        print(flag)
    else:
        print("That didn't work, try again!")