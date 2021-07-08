from construct import *
from hashlib import sha256
from binascii import hexlify
import time
import struct

INITIAL_KEYS = [b"asd"+b"\x00"*29, b"def"+b"\x00"*29, b"hij"+b"\x00"*29]

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
        self.skey = INITIAL_KEYS[p_num]
        self.skey_num = 0
        self.transport = None

        self.GenericMessageHeader = Struct(
            'directive' / Int32ul,
            'key'       / Bytes(32),
            'mlen'      / Int32ul
        )

        # self.generate_key()
    
    def initialize_transport(self, t):
        self.transport = t

    def answer_question(self, d):
        return 1

    # Determine what the interface is asking for and use its message to provide it the information it needs
    def handle_msg(self, msgHeader, msg):
        print(f"Voter_{self.identity} -- Got directive: {hex(msgHeader.directive)} | msg: {hexlify(msg)} | data len: {msgHeader.mlen}")

        if msgHeader.directive == Voter.MSG_RESPONSE or msgHeader.directive == Voter.VOTER_VOTE or msgHeader.directive == Voter.VOTER_READY:
            msg = struct.unpack("<I", msg[0:4])[0]
            if msg > 0:   # TODO change to bool or to constant
                self.update_key()
                print("Moving hash forward")
                print(f"New key: {hexlify(self.skey)}")

        if msgHeader.directive == Voter.POSE_QUESTION:
            print("Voter got a question")

            time.sleep(2.5)

            # Unpack the data
            d = struct.unpack("<ddddddd", msg)
            a = self.answer_question(d)

            msg = self.create_msg(struct.pack("<I", a), Voter.VOTER_VOTE)
            return msg

        return None
    
    def create_msg(self, msg, d):
        print(f"key: {hexlify(self.skey)}")

        msg_size = len(msg)  # directive, key, length of header+msg, msg
        full_msg_packed = struct.pack(f"<I32sI", d, self.skey, msg_size) + msg

        print(f"Creating message with len {len(full_msg_packed)}: {hexlify(full_msg_packed)}")

        return full_msg_packed

    def update_key(self):
        self.skey = ( sha256(self.skey).digest() )

    def calc_next_value(self):
        return

    def vote_value(self):
        return
