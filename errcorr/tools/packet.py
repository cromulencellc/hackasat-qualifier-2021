import os
import numpy as np
import sys

UPSAMPLING_MULTIPLIER = 4


def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


if __name__ == "__main__":

    number_of_arguments = len(sys.argv)

    number_of_total = 0

    try:
        if number_of_arguments == 2:
            number_of_total = int(sys.argv[1])
        elif number_of_arguments == 1:
            number_of_total = 1
        else:
            number_of_total = 0
            print("Wrong number of arguments. Try again.\n")
            exit(1)
    except Exception as e:
        print(f"Exception: {e}\n")
        exit(2)

    flag = 'flag{TESTflag1234}'
    the_len = len(flag) - 1
    the_len_bin = '{0:016b}'.format(the_len)
    flag_in_bits = text_to_bits(flag)

    preamble = '00011010110011111111110000011101'  # 1ACFFC1D
    pvn = '000'
    pkt_type = '0'
    sec_hdr_flag = '0'
    apid = '00000000001'
    seq_flags = '11'
    pkt_seq_cnt_or_pkt_name = '00000000000000'

    total = pvn + pkt_type + sec_hdr_flag + apid + seq_flags + pkt_seq_cnt_or_pkt_name + the_len_bin + flag_in_bits

    total = preamble + total

    # total_multiple = number_of_total * total

    total_multiple = number_of_total * '01010101' + total + number_of_total * '01010101'

    f = open("packet.txt", "w")
    # f.write(total)
    f.write(total_multiple)
    f.close()

    exit(0)

