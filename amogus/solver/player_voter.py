#!/usr/bin/env python3

import asyncio
import argparse
import logging
import socket
import binascii
import time
import json
import aioconsole
import codecs
import sys
import struct

from binascii import hexlify
from construct import *
from ctypes import sizeof, c_int

FLAG = "flag{this_is_very_suspicious}"

INITIAL_KEYS = [b"", b"", b"05f1e0f77ce8fbb75532e8023056e4e6"]
MESSAGE_HEADER_LEN = sizeof(c_int) + 32 + sizeof(c_int)
SERVER_PORT = 31337
VOTER_NUM = 2

LOG_LEVEL = logging.ERROR
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=LOG_LEVEL)
logger = logging.getLogger(__name__)

class VoterClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost, voter_num, loop):
        self.voter = Voter(voter_num)
        self.transport = None
        self.on_con_lost = on_con_lost
        self.loop = loop

    def connection_made(self, transport):
        self.voter.initialize_transport(transport)  # Initialize transport object in voter object
        peername = transport.get_extra_info('peername') # Get the IP and port we just connected to

        logging.debug(f"Made new connection {peername[0]} : {peername[1]}\n")

        self.transport = transport # Intialize transport object so we can send stuff outside this function

        return

    def data_received(self, data):
        while len(data) > 0:
            if len(data) >= MESSAGE_HEADER_LEN:
                try:
                    msgHeader = self.voter.GenericMessageHeader.parse(data[0:MESSAGE_HEADER_LEN])
                except StreamError as e:
                    logging.warning(f"Error while trying to parse message from interface: {str(e)}")
                    return

                logger.debug(f"len: {len(data)} | Data: {data.hex()}\n")

                full_msg = data[0:MESSAGE_HEADER_LEN+msgHeader.mlen]
                header = data[0:MESSAGE_HEADER_LEN]
                msg = data[MESSAGE_HEADER_LEN:MESSAGE_HEADER_LEN+msgHeader.mlen]
                data = data[MESSAGE_HEADER_LEN+msgHeader.mlen:]

                logger.debug(f"RECV from interface: [directive:{msgHeader.directive}][key:{hexlify(msgHeader.key)}][mlen:{msgHeader.mlen}] msg:{msg.hex()} | data: {data.hex()}")

                self.loop.create_task((self.voter.handle_msg(msgHeader, header, msg, full_msg)))
                
                logger.debug(f"End: {len(data)}")
            else:
                logger.debug(f"Received too small of a message: {hexlify(data)}...")

    def connection_lost(self, exc):
        logger.info('The server closed the connection')
        self.on_con_lost.set_result(True)

class Voter():

    # Directive Constants
    POSE_QUESTION     = 0
    VOTER_VOTE        = 1
    MSG_RESPONSE      = 2
    VOTER_LOG_CACHE   = 3
    VOTER_LOG_SAVE    = 4
    VOTER_READY       = 5
    INVALID_DIRECTIVE = 99

    MSG_SUCCESS       = 1
 
    def __init__(self, p_num):
        self.transport = None
        self.answers_file = None
        self.answer = [0.0, 0.0, 0.0, 0.0]
        self.last_commit = b""
        self.last_answer = b""
        self.count = 0
        self.answers = None
        self.lock = asyncio.Lock()

        with open("answer_index.txt", "r") as f:
            self.answers = json.load(f)

        self.GenericMessageHeader = Struct(
            'directive' / Int32ul,
            'key'       / Bytes(32),
            'mlen'      / Int32ul
        )
    
    def initialize_transport(self, t):
        self.transport = t

    # Determine what the interface is asking for and use its message to provide it the information it needs
    async def handle_msg(self, msgHeader, header, msg, full_msg):
        logger.debug(f"Voter_PLAYER -- Got directive: {hex(msgHeader.directive)} | msg: {hexlify(msg)} | data len: {msgHeader.mlen}")
        
        if msgHeader.directive == Voter.POSE_QUESTION and msgHeader.key == b"\xFF"*32:
            if(self.last_commit != self.last_answer):
                # print(f"Last commit: {self.last_commit} | last_answer: {self.last_answer}")
                self.count += 1
            else:
                self.count = 0

            if(self.count > 5):
                sys.stdout.write(FLAG)
                sys.stdout.flush()

            key = msg.hex()
            if(key in self.answers):
                # print(f"Last answer: {self.last_answer}")
                self.last_answer = struct.pack("<dddd", *self.answers[key])
            else:
                # print(f"Last answer?: {self.last_answer}")
                self.last_answer = struct.pack("<dddd", *[0.992, 0.123, 0.0, 0.0])
        
        if msgHeader.directive == Voter.VOTER_VOTE:
            if(msgHeader.key == b"\xFF"*32):    # Got confirmation of commit
                self.last_commit = msg

        sys.stdout.write(full_msg.hex() + "\n")
        sys.stdout.flush()

        return

async def main():

    parser = argparse.ArgumentParser(description="Sping up an instance of a voter for the Among Us challenge")

    parser.add_argument('-i',
                        '--identity',
                        metavar="1234",
                        type=int,
                        help="Voter number",
                        default=2)
    parser.add_argument('-p',
                        '--port',
                        metavar='65536',
                        default=31337,
                        type=int,
                        help='Port to connect to interface on')


    args = parser.parse_args()

    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()

    while True:
        try:
            transport, protocol = await loop.create_connection(
                lambda: VoterClientProtocol(on_con_lost, args.identity, loop),
                'localhost', SERVER_PORT)
            break
        except socket.error as e:
            logging.error(f"Interface is not up... got {str(e)}")
            logging.error("Trying again in 3 seconds...")
            time.sleep(3)

    key = INITIAL_KEYS[2]

    sys.stdout.flush()
    sys.stdout.write("************Among Us************\n")
    sys.stdout.flush()
    sys.stdout.write(f"Your key: {key.hex()}\n")
    sys.stdout.flush()
    
    try:
        await on_con_lost
    except KeyboardInterrupt:
        transport.close()
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())