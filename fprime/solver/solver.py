import sys
import socket
import os
import subprocess
import time


if __name__ == "__main__":
    host = os.environ.get('CHAL_HOST')
    port = os.environ.get('CHAL_PORT')

    ticket = os.environ.get('TICKET', "")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, int(port)))

    fsock = sock.makefile('rw')
    if len(ticket):
        fsock.readline()
        fsock.write(ticket + '\n')
        fsock.flush()
    _ = fsock.readline()
    _ = fsock.readline()
    line = fsock.readline()

    print(line)
    host,port = line.rstrip().split('/')[-1].split(":")
    print(host, port)
    env = os.environ
    env['CHAL_HOST'] = host
    env['CHAL_PORT'] = port
    print("Sleeping to let the system boot for 30sec...")
    time.sleep(30)

    process = subprocess.Popen(["/bin/bash", '-c', './solver.sh 2>&1'], env=env)

    process.wait()