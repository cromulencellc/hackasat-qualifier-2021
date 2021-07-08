#!/bin/sh

python qpsk_ccsds_demod.py
python3 shifttester.py /out/out.bin

