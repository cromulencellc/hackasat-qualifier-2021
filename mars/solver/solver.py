#!/usr/bin/python3

from websocket import create_connection
import socket
import os
import json
import http
import time
import sys

def do_sim(ws):

    print("[INFO] Starting the simulation")

    ws.send('{"cmd":"start"}')

    print("[INFO] Receiving data.", end='')
    while True:

        try:
            data = ws.recv()
            message = json.loads(data)
            print('.', end='')
            sys.stdout.flush()

        except:
            return False
        
        if message['type'] == 'result':

            print("\n[INFO] Got the end of the simulation")

            status = message['status']

            if status == 'success':
                print("[SUCCESS] The simulation completed successfully!")
                print(message['message'])
                return True
            else:
                print("[FAIL] Simulation did not work")
                return False

    return True

def main():



    if 'CHAL_HOST' in os.environ and 'CHAL_PORT' in os.environ:
        host = os.environ.get('CHAL_HOST')
        port = os.environ.get('CHAL_PORT')
        ticket = os.environ.get('TICKET', "")
    else:
        print('[ERROR] CHAL_HOST and CHAL_PORT environment variables are required')
        exit(-1)
    
    # Get the host:port from LCM 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, int(port)))
    fsock = sock.makefile('rw')
    if len(ticket):
        fsock.write(ticket + '\n')
        fsock.flush()
    line =  fsock.readline()
    line =  fsock.readline()
    line =  fsock.readline()
    print(line)
    host,port = line.rstrip().split('/')[-1].split(" ")[-1].split(":")

    print("[INFO] Retrieving the ROM image")

    time.sleep(2)
    h1 = http.client.HTTPConnection(host, port)

    h1.request("GET","/bad.rom")

    response = h1.getresponse()

    data = response.read()

    print("[INFO] Received {} bytes of data".format(len(data)))

    mutable = bytearray(data)

    print("[INFO] Patching the ROM image")
    mutable[0x5820:0x5824] = b'\x26\x00\xc0\xa3'

    data = bytes(mutable)
    
    connect_string = "ws://{}:{}".format(host, port)

    try:
        ws = create_connection(connect_string, timeout = 15)

    except:
        print("[ERROR] Unable to open websocket to {}".format(connect_string))
        exit(-1)

    print("[INFO] Connected to the service")

    print("[INFO] Sending the patched ROM image")

    message = {'cmd':'upload','data': data.decode('latin-1') }

    string = json.dumps(message, ensure_ascii=False)

    ws.send(string)

    # delay to give nodejs time to write the new image to disk
    time.sleep(1.0)

    if do_sim(ws) == False:

        exit(-1)

    exit(0)

if __name__ == "__main__":
    main()
