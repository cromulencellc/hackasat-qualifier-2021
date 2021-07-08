#!/usr/bin/env python3

import asyncio
import argparse
import logging
import socket
import struct
import time
import random
import json

import numpy as np
from scipy.spatial.transform import Rotation as R

from binascii import hexlify
from construct import *
from ctypes import sizeof, c_int
from hashlib import sha256

INITIAL_KEYS = [b"e9b9d3f2d275ca5759e60c8ee18425dc", b"f58ebfe38a88eb2d760e64acb062585f", b"05f1e0f77ce8fbb75532e8023056e4e6"]
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

        logging.info(f"Made new connection {peername[0]} : {peername[1]}\n")

        self.transport = transport # Intialize transport object so we can send stuff outside this function

        message = self.voter.create_msg(b"", Voter.VOTER_READY)
        transport.write(message)
        logger.info(f"Sending VOTER_READY message to interface: data ({len(message)} bytes): {hexlify(message)}")

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

                msg = data[MESSAGE_HEADER_LEN:MESSAGE_HEADER_LEN+msgHeader.mlen]
                data = data[MESSAGE_HEADER_LEN+msgHeader.mlen:]

                logger.debug(f"RECV from interface: [directive:{msgHeader.directive}][key:{hexlify(msgHeader.key)}][mlen:{msgHeader.mlen}] msg:{msg.hex()} | data: {data.hex()}")

                self.loop.create_task((self.voter.handle_msg(msgHeader, msg)))
                
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
        self.identity = p_num
        self.skey_list = [] # array of bytearrays
        self.skey = INITIAL_KEYS[self.identity]
        self.skey_num = 0
        self.transport = None
        self.answers_file = None
        self.answer = [0.0, 0.0, 0.0, 0.0]
        self.lock = asyncio.Lock()
        self.commit = b""
        self.voted = False

        self.count = 0

        with open("answer_index.txt", "r") as f:
            self.answers = json.load(f)

        self.GenericMessageHeader = Struct(
            'directive' / Int32ul,
            'key'       / Bytes(32),
            'mlen'      / Int32ul
        )
    
    def initialize_transport(self, t):
        self.transport = t

    def answer_question(self, d=None):
        answer = self.answers_file.readline().strip('\n').split(',')[1:]
        for i in range(0,len(answer)):
            try:
                answer[i] = float(answer[i])
            except ValueError as e:
                logger.warning("Got value error parsing answer from file... Sending back random values")
                answer = [1.0, 0.2, 0.0, 0.0]
        return answer

    # Determine what the interface is asking for and use its message to provide it the information it needs
    async def handle_msg(self, msgHeader, msg):
        logger.debug(f"Voter_{self.identity} -- Got directive: {hex(msgHeader.directive)} | msg: {hexlify(msg)} | data len: {msgHeader.mlen}")

        if msgHeader.directive == Voter.MSG_RESPONSE:
            msg = struct.unpack("<I", msg)[0]
            if msgHeader.key != b"\xFF"*32 and msg == Voter.MSG_SUCCESS:   # TODO change to bool or to constant
                self.update_key()
                logging.debug("Moving hash forward")
                logger.debug(f"New key: {hexlify(self.skey)}")

        if msgHeader.directive == Voter.POSE_QUESTION and msgHeader.key == b"\xFF"*32:
            logger.info("Voter got a question")
            async with self.lock:
                self.voted = False
                self.commit = None

            # Unpack the data
            # TODO: Throw in try except

            key = msg.hex()
            if key in self.answers:
                self.answer = self.answers[key]
            else:
                self.answer = [0.992, 0.123, 0.0, 0.0]
            
            await asyncio.sleep(0.5 + random.random())

            async with self.lock:
                if self.voted == True or self.commit:   # We already voted or we agree w the answer committed
                    pass
                else:
                    msg = self.create_msg(struct.pack("<dddd", *self.answer), Voter.VOTER_VOTE)
                    self.transport.write(msg)
                    self.voted = True
        
        if msgHeader.directive == Voter.VOTER_VOTE:
            if(msgHeader.key == b"\xFF"*32):    # Got confirmation of commit
                logger.debug(f"New commit: {msg.hex()}")
                async with self.lock:
                    if not (msg == struct.pack("<dddd", *self.answer)):
                        logger.debug(f"Got {struct.unpack('<dddd', msg)} vs {self.answer}")
                        msg = self.create_msg(struct.pack("<dddd", *self.answer), Voter.VOTER_VOTE)
                        self.transport.write(msg)
                        self.voted = True
                    else:
                        self.commit = msg
            else:   # Got confirmation of vote
                logging.debug("Moving hash forward")
                self.update_key()
                logger.debug(f"New key: {hexlify(self.skey)}")

        return
    
    def create_msg(self, msg, d):
        logging.info(f"key: {hexlify(self.skey)}")

        msg_size = len(msg)  # directive, key, length of header+msg, msg
        full_msg_packed = struct.pack(f"<I32sI", d, self.skey, msg_size) + msg

        logger.debug(f"Creating message with len {len(full_msg_packed)}: {hexlify(full_msg_packed)}")

        return full_msg_packed

    def update_key(self):
        self.skey = ( sha256(self.skey).digest() )

class PlayerVoter(Voter):
    def __init__(self, p_num):
        super().__init__(p_num)
        return

async def main():

    parser = argparse.ArgumentParser(description="Sping up an instance of a voter for the Among Us challenge")

    parser.add_argument('-i',
                        '--identity',
                        metavar="1234",
                        type=int,
                        help="Voter number",
                        default=0)
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

    try:
        await on_con_lost
    except KeyboardInterrupt:
        transport.close()
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())