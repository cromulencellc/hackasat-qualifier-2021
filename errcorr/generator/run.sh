#!/bin/sh

python3 packet_2.py
cp packet.bin /out/.
python qpsk_ccsds.py
rm /out/packet.bin

