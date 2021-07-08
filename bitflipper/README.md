# Quals Challenge: Bit Flipper #

**Category:** We're On the Same Wavelength
**Relative Difficulty:** 4/5
**Author:** [Cromulence](https://cromulence.com/)

You've been provided a special capability to target ionizing radiation on a region of memory used by a spacecraft's thermal protection system (TPS). Use this ability to flip the right combination of 3 bits that will pass SECDED checks, and change the behavior of the spacecraft's TPS when decoded from memory. Referring to the memory in its encoded form (encoded.bin), you must select a byte (0-404) and then which bit (0-7) in the byte to flip. You are allowed 3 bit flips.

Effect a change in the TPS such that the spacecraft exceeds its operating temperature range of 0-70C to obtain the flag.

```
For example:
Byte 4 (0x6d) = 01101101    (0x6d)
Bit 3                ^
New Byte      = 01101001    (0x69)

Encoded Bytes (also provided in encoded.bin):
00000000: 2320 5465 6d70 6572 b6  # Temper.
00000009: 6174 7572 6520 5365 b5  ature Se.
00000012: 6e73 6f72 0a23 2049 52  nsor.# IR
0000001b: 6620 7465 6d70 6572 b9  f temper.
00000024: 6174 7572 6520 6162 ba  ature ab.
0000002d: 6f76 652f 6265 6c6f 70  ove/belop
00000036: 7720 7468 7265 7368 4b  w threshK
0000003f: 6f6c 642c 2064 6561 5d  old, dea]
00000048: 6374 6976 6174 652f 5b  ctivate/[
00000051: 6163 7469 7661 7465 ae  activate.
0000005a: 2068 6561 7465 720a 54   heater.T
00000063: 696d 706f 7274 2073 50  import sP
0000006c: 7973 0a0a 6465 6620 2b  ys..def +
00000075: 7265 6164 5465 6d70 3d  readTemp=
0000007e: 2874 656d 702c 7374 9f  (temp,st.
00000087: 6174 6529 3a0a 2020 ac  ate):.  .
00000090: 2020 6966 2074 656d 42    if temB
00000099: 7020 3c20 3135 2061 d4  p < 15 a.
000000a2: 6e64 206e 6f74 2073 7e  nd not s~
000000ab: 7461 7465 3a0a 2020 92  tate:.  .
000000b4: 2020 2020 2020 7072 46        prF
000000bd: 696e 7428 2254 656d e3  int("Tem.
000000c6: 703a 2025 2e32 6643 f1  p: %.2fC.
000000cf: 2041 6374 6976 6174 79   Activaty
000000d8: 696e 6720 6865 6174 68  ing heath
000000e1: 6572 2225 7465 6d70 4c  er"%tempL
000000ea: 290a 2020 2020 2020 85  ).      .
000000f3: 2020 7265 7475 726e fa    return.
000000fc: 2031 0a20 2020 2065 f3   1.    e.
00000105: 6c69 6620 7465 6d70 34  lif temp4
0000010e: 203e 2033 3520 616e 69   > 35 ani
00000117: 6420 7374 6174 653a 4d  d state:M
00000120: 0a20 2020 2020 2020 80  .       .
00000129: 2070 7269 6e74 2822 64   print("d
00000132: 5465 6d70 3a20 252e 76  Temp: %.v
0000013b: 3266 4320 4465 6163 c6  2fC Deac.
00000144: 7469 7661 7469 6e67 81  tivating.
0000014d: 2068 6561 7465 7222 d9   heater".
00000156: 2574 656d 7029 0a20 a2  %temp). .
0000015f: 2020 2020 2020 2072 40         r@
00000168: 6574 7572 6e20 300a d6  eturn 0..
00000171: 2020 2020 656c 7365 cb      else.
0000017a: 3a0a 2020 2020 2020 3f  :.      ?
00000183: 2020 7265 7475 726e fa    return.
0000018c: 2073 7461 7465 0a0a c2   state...
```

## Running Challenge ##
Create and run the challenge container `bitflipper:challenge`
```sh
make challenge
nc localhost 12345
```

## Running Solver ##
Create and run the solver container `bitflipper:solver` against the challenge container `bitflipper:challenge`
```sh
make solver
```
