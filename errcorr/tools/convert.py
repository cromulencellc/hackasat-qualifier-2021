import sys
import math
# import binascii
# import codecs


# Nomenclature for using this file:
#
# python convert.py <string of 0’s and 1’s> <output filename>  (writes 0’s and 1’s as binary to the output filename)
#
# python convert.py <input file of a string of 0’s and 1’s> <output filename> (writes string of 0’s and 1’s from input
#                                                                              file as binary to the output filename>)
#
# python convert.py <binary filename of binary 0’s and 1’s>  (writes the binary data as a string of 0’s and 1’s)

def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'


def handle_file_input3(filename):
    with open(filename, 'rb') as fp:
        line = fp.readline()

        line = line.hex()

        len_1 = len(line) * math.log2(16)

        line = bin(int(line, 16))[2:]

        len_2 = len(line)

        number_of_leading_zeros = len_1 - len_2

        leading_zeros = "0" * int(number_of_leading_zeros)

        line = leading_zeros + line

        print(line)


def handle_file_input5(input_filename, output_filename):
    with open(input_filename, 'rb') as fp:
        line = fp.readline()

        decimal_representation = int(line, 2)

        the_hex_string = hex(decimal_representation)

        the_hex_string = the_hex_string[2:]

        bin_data = bytes.fromhex(the_hex_string)

        buf = bytearray(0)

        for byte in bin_data:
            buf.append(int.from_bytes([byte], byteorder="little", signed=False))

        f = open(output_filename, 'wb')
        f.write(buf)
        f.close()


def handle_string_input2(the_string, the_file):
    decimal_representation = int(the_string, 2)

    the_hex_string = hex(decimal_representation)

    the_hex_string = the_hex_string[2:]

    bin_data = bytes.fromhex(the_hex_string)

    buf = bytearray(0)

    for byte in bin_data:
        buf.append(int.from_bytes([byte], byteorder="little", signed=False))

    f = open(the_file, 'wb')
    f.write(buf)
    f.close()


def main():
    number_of_arguments = len(sys.argv) - 1

    if number_of_arguments == 1:

        filename = sys.argv[1]

        if '.' in filename:
            handle_file_input3(filename)
        else:
            print("The first argument must be a filename.")

    elif number_of_arguments == 2:

        arg1 = sys.argv[1]
        arg2 = sys.argv[2]

        if '.' in arg1 and '.' in arg2:
            handle_file_input5(arg1, arg2)
        elif '.' not in arg2:
            print("The second argument must be a filename.")
        else:
            handle_string_input2(arg1, arg2)

    else:
        print("An incorrect number or arguments were entered.")


if __name__ == '__main__':
    main()
