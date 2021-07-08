import os
import socket
import numpy as np
import matplotlib.pyplot as plt
import time

the_flag = ""
DOWNSAMPLING_MULTIPLIER = 4


def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    val = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'
    return val


# Function to determine the quadrant of a complex number
def quadrant(s):
    if s == "":
        return

    len_of_s = len(s)

    if '+' in s:
        i = s.index('+')
    else:
        i = s.rindex('-')

    # Get the real part of the complex number.
    real = s[0:i]

    # Get the imaginary part of the complex number.
    imaginary = s[i:len_of_s - 1]

    imaginary = imaginary.translate({ord('j'): None})

    x = float(real)
    y = float(imaginary)

    if x > 0 and y > 0:
        return 4
    elif x < 0 and y > 0:
        return 1
    elif x < 0 and y < 0:
        return 2
    elif x > 0 and y < 0:
        return 3
    elif x == 0 and y > 0:
        return 0
    elif x == 0 and y < 0:
        return 0
    elif y == 0 and x < 0:
        return 0
    elif y == 0 and x > 0:
        return 0
    else:
        return 0


if __name__ == "__main__":

    try:
        f = open('/data/iqdata.txt', 'r')

        received = f.read()

        s = received.split('\n')

        packet = ''

        for element_index in range(1, len(s), DOWNSAMPLING_MULTIPLIER):

            # print(s[element_index])

            q = quadrant(s[element_index])

            if q == 0:
                print("Indeterminate symbol - cannot demodulate.\n")
                exit(1)
            else:
                if q == 1:
                    packet += '00'
                elif q == 2:
                    packet += '01'
                elif q == 3:
                    packet += '10'
                elif q == 4:
                    packet += '11'

        user_data_length = packet[64:80]
        decimal_representation = int(user_data_length, 2)
        hexidecimal_string = hex(decimal_representation)
        flag_length = int(hexidecimal_string, 16)
        flag_length += 1
        the_flag = packet[81:81 + (flag_length * 8)]
        var = text_from_bits(the_flag)
        print(var)

    except Exception as e:
        print("An error occurred.\n")
        print(e)
