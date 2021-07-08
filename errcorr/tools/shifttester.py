import os
import socket
import numpy as np
import matplotlib.pyplot as plt
import time
import math
import sys


# def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
def text_from_bits(bits, encoding='utf-8', errors='ignore'):

    try:
        n = int(bits, 2)
        val = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'
        return val
    except Exception as e:
        # print(f"An exception occurred in text_from_bits() - {e}\n")
        return None


def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


flag = 'flag{TESTflag1234}'


if __name__ == "__main__":

    try:

        flag_bits = text_to_bits(flag)

        # filename = 'out.bin'
        # filename = 'packet.bin'

        filename = sys.argv[1]


        number_of_bytes_to_read_at_a_time = 128
        shift_window_width = 100

        fp = open(filename, 'rb')

        while True:

            line = fp.read(number_of_bytes_to_read_at_a_time)

            if len(line) == 0:
                break

            line = line.hex()
            # print(line)

            line = bin(int(line, 16))[2:]

            for i in range(0, len(line), 1):
                try:
                    string = line[i-shift_window_width:i+shift_window_width]

                    var = text_from_bits(string)

                    if 'flag' in var:
                        print(var)
                        # print("Congratulations! You recovered the flag!\n")
                        # exit(0)

                except Exception as e:
                    continue

        fp.close()

    except Exception as e:
        print("An error occurred.\n")
        print(e)
