import os
import numpy as np

UPSAMPLING_MULTIPLIER = 4


def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


if __name__ == "__main__":

    flag = os.getenv("FLAG")
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

    num_symbols = int(len(total) / 2)
    x_int = []

    for i in range(0, int(num_symbols * 2) - 1, 2):
        var = total[i] + total[i + 1]
        val = int(var, 2)

        for j in range(0, UPSAMPLING_MULTIPLIER):
            x_int.append(val)

    x_degrees = [x * 360.0 / 4.0 + 45.0 + 90.0 for x in x_int]

    x_radians = [x * np.pi / 180.0 for x in x_degrees]

    x_symbols = np.cos(x_radians) + 1j * np.sin(x_radians)

    n = (np.random.randn(num_symbols * UPSAMPLING_MULTIPLIER) + 1j * np.random.randn(num_symbols * UPSAMPLING_MULTIPLIER)) / np.sqrt(2)

    noise_power = 0.05
    r = x_symbols + n * np.sqrt(noise_power)

    f = open('/out/iqdata.txt', 'w+')

    for x in range(len(r)):
        s = str(r[x])

        s = s.translate({ord('('): None})
        s = s.translate({ord(')'): '\n'})

        f.write(s)

    f.close()
