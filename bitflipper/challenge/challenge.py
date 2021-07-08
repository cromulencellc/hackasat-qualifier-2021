# BitFlipper Challenge
import os, sys
from time import sleep
from timeout import timeout, TimeoutError

time = int(os.getenv("TIMEOUT",90))

sensorFile = 'sensor.py'
encodedFile = 'encoded.bin'
decodedFile = 'decoded.py'

def render_intro():
    art = [
        "   BIT FLIPPER\n",
        "    CHALLENGE\n\n",
        "            1\r",
        "           11\r",
        "          011\r",
        "         0011\r",
        "        00011\r",
        "       000011\r",
        "      1000011\r",
        "     01000011\r",
        "     11000011\r",
        "     10000011\r",
        "     10100011\r",
        "     10110011\r",
        "     10111011\r",
        "     10111111\r",
        "     10111101\r",
        "     10111100\n",
    ]
    # Challenge Intro
    for row in art:
        print(row,end='')
        sleep(0.25)
        sys.stdout.flush()

    print("\nYou've been provided a special capability to target ionizing radiation on a region of memory used by a spacecraft's thermal protection system (TPS). Use this ability to flip the right combination of 3 bits that will pass SECDED checks, and change the behavior of the spacecraft's TPS when decoded from memory. Refering to the memory in its encoded form (encoded.bin), you must select a byte (0-404) and then which bit (0-7) in the byte to flip. You are allowed 3 bit flips.")
    print("\nEffect a change in the TPS such that the spacecraft exceeds its operating temperature range of 0-70C to obtain the flag.\n")

def pack(u):
    p = bytearray(int(len(u)/8))
    i = len(u)/8-1
    j = 0
    while i >=0:
        k = 0
        while k < 8:
            p[j] = (u[int(8*i)+k] << k) ^ p[j]
            k = k+1
        i -= 1
        j += 1
    return p

# Unpack bytearray p
def unpack(p):
    u = bytearray(8*len(p))
    i = len(p)-1
    j = 0
    while i >= 0:
        cByte = p[i] # current byte
        k = 0
        while k < 8:
            mask = 1 << k
            cBit = (mask & cByte) >> k # current bit
            u[j] = cBit
            j += 1
            k += 1
        i -= 1
    return u

# Encode
def encode(d):
    # This funcrtion performs Hamming (72,64) encoding according to the following scheme:
    # systemic form                                                                 parity
    # hex:  1a       cf       fc       1d       ff       ff       ff       ff       87654321
    # bin:  00011010 11001111 11111100 00011101 11111111 11111111 11111111 11111111  1011001  no extra parity bit
    # bin:  00011010 11001111 11111100 00011101 11111111 11111111 11111111 11111111 11011001  extra parity bit
    # pos:  43210987 65432109 87654321 09876543 21098765 43210987 65432109 87654321
    # pos:  66666555 55555554 44444444 43333333 33322222 22222111 11111110 00000000

    # reverse bit order before interleaving...
    # pos:  00000000 01111111 11122222 22222333 33333334 44444444 45555555 55566666 6666677
    # pos:  12345678 90123456 78901234 56789012 34567890 12345678 90123456 78901234 5678901
    # bit:  11111111 11111111 11111111 11111111 10111000 00111111 11110011 01011000
    
    # interleave for encoding
    # enc:  ppdpdddp dddddddp dddddddd dddddddp dddddddd dddddddd dddddddd dddddddp ddddddd
    # bit:  pp1p111p 1111111p 11111111 1111111p 11111110 11100000 11111111 1100110p 1011000 
    
    # p1 =  p 1 1 1  1 1 1 1  1 1 1 1  1 1 1 1  1 1 1 1  1 1 0 0  1 1 1 1  1 0 1 0  1 1 0 0     29 -> 1   
    # p2 =   p1  11   11  11   11  11   11  11   11  11   11  00   11  11   10  10   01  00     28 -> 0
    # p4 =     p111     1111     1111     1111     1111     0000     1111     0110     1000     26 -> 0
    # etc... for p8, p16, p32, and p64

    # Ensure data bytearray contains 8 bytes. Fill unused bytes with \n
    while len(d) < 8:
        d = d + b'\x0a'
    
    # Unpacked data, parity, and encoded bytearrays
    ud = unpack(d)      #unpacked data bits
    ui = bytearray(71)  #unpacked, interleaved, i.e. p1p2d1p3d2d3d4...d64, ignore extra parity bit
    us = bytearray(71)  #unpacked, systemic, i.e. p1...p8d1...d64, ignore extra parity bit

    # Populate interleaved bytearray with data bits first
    i = 1
    id = 1
    ip = 1
    while i <= len(ui):
        if i == ip:
            #ui[i-1] = 0 # initialize parity bits to 0
            ip = ip << 1
        else:
            ui[i-1] = ud[id-1]
            id += 1
        i += 1

    # Calculate parity bits
    up = bytearray(8)   #unpacked parity bits
    i = 0
    ip = 1
    while i < 7:
        j = 1 # bit position in ui
        for b in ui:
            # if j has 1 in ip significant position
            if ip & j:
                # if data bit is 1
                if b:
                    up[i] = up[i] ^ 1 # flip bit (even parity)
            j += 1
        i += 1
        ip = ip << 1
    
    # Populate interleaved bytearray with parity bits
    i = 1
    j = 0
    ip = 1
    while i <= len(ui):
        if i == ip:
            ui[i-1] = up[j] 
            ip = ip << 1
            j += 1

        # Calculate extra parity bit along the way
        if ui[i-1]:
            up[7] = up[7] ^ 1
        i += 1

    # Pack parity bits
    p = pack(up)

    # Convert to systemic form
    e = d + p
    
    return bytearray(e)

# Single error correction, double error detection
def secded(ui):
    up = bytearray(8) #unpacked parity bits received
    upC = bytearray(8) #unpacked parity bits check
    p8err = False # extra parity bit error?

    # Check extra parity bit
    i = 0
    while i < len(ui)-1:
        upC[7] = upC[7] ^ ui[i]
        i += 1
    if upC[7] != ui[71]:
        p8err = True
    
    # Interleaved form, parity check
    # 10101111 11111111 11111111 11111110 11111110 11100000 11111111 11001101 10110001 sent
    # 10101111 11111111 11111111 11111110 11111110 11100000 11111110 11001101 10110001 received
    #                                                              ^ (56 is flipped)

    # ...p111. ...1111. ...1111. ...1111. ...1111. ...0000. ...1111. ...0110. ...1000e 26 -> 0 = p4
    # .......p 1111111. .......1 1111111. .......0 1110000. .......0 1100110. .......e 22 -> 0 = p8
    # ........ .......p 11111111 1111111. ........ .......0 11111110 1100110. .......e 

    # Check remaining parity bits
    i = 0
    ip = 1
    while i < 7:
        j = 1 # bit position in ui
        for b in ui[0:71]:
            # if parity bit, extract and dont include in calculation
            if j == ip:
                up[i] = ui[j-1] # extract received parity bits
            # if index j is a data bit covered by the current parity bit index ip
            if ip & j and j != ip:
                # if data bit is 1
                if b:
                    upC[i] = upC[i] ^ 1 # flip bit (even parity)
            j += 1
        i += 1
        ip = ip << 1
    


    p = pack(up) # packed parity bits received
    pC = pack(upC) # packed parity bits check
    pC[0] = pC[0] & 127 # Ignore overall parity bit for XOR check
    p[0] = p[0] & 127 # Ignore overall parity bit for XOR check
    pos = pC[0] ^ p[0]

    if not pos and not p8err:
        #print("SECDED: no errors")
        return ui
    elif pos and p8err:
        print("SECDED: single error corrected (data)")
        ui[pos-1] = ui[pos-1] ^ 1 # correct the bit
    elif not pos and p8err:
        print("SECDED: single error corrected (extra parity bit)")
    elif pos and not p8err:
        print("SECDED: single error corrected (data)")
        ui[pos-1] = ui[pos-1] ^ 1 # correct the bit
    else:
        print("SECDED: double error detected")
        return 0

    return ui


# Decode
def decode(e):
    d = e[0:8]
    p = e[8:9]

    ud = unpack(d)
    up = unpack(p)
    ui = bytearray(72)

    # Populate interleaved bytearray
    i = 1
    id = 1
    ip = 1
    k = 0
    while i <= len(ui)-1:
        if i == ip:
            ui[i-1] = up[k]
            k += 1
            ip = ip << 1
        else:
            ui[i-1] = ud[id-1]
            id += 1
        i += 1
    ui[71] = up[7]
    
    # Perform SECDED
    ui = secded(ui)

    #Convert to systemic but only need data bits
    i = 1
    id = 1
    ip = 1
    k = 0
    while i <= len(ui)-1:
        if i == ip:
            up[k] = ui[i-1]
            k += 1
            ip = ip << 1
        else:
            ud[id-1] = ui[i-1]
            id += 1
        i += 1

    d = pack(ud)
    #p = pack(up)
    
    return bytearray(d)

@timeout(time)
def ionize(i):
    encFile = open('encoded.bin', 'r+b')
    
    print("Bitflip #",i,sep='')
    offset = int(input("   Select byte to ionize (0-404): "))
    shift =  int(input("   Select bit to ionize (0-7):    "))

    sys.stdout.flush
    
    encFile.seek(offset)
    data = int.from_bytes(encFile.read(1), "big")

    mask = 1 << shift
    data = mask ^ data
    data = data.to_bytes(1,'big')

    encFile.seek(offset)
    encFile.write(data)
    encFile.close()

def simulate():
    # Simulate active thermal management with some spacecraft temperature sensor
    # Q = m*c*(T1-T0)
    # T1 = Q/(m*c)+T0
    m = 0.2 #kg
    c = (0.897+0.710+0.385)/3 * 1000 # J/(kg*K) some mixture of aluminum, graphite, and copper
    T = 25 # Initialize to 25 degrees Celsius
    i = 0
    qEnv = 1370 * 0.01 # Watts, 1% of solar flux in Earth orbit for a 1m^2 satellite
    qRad = qEnv * 1.10 # Watts, dissipate 10% more than solar flux
    qHeater = 0
    dt = 1 # seconds
    heaterOn = 0
    while i < 3600:
        Q = (qEnv + qHeater - qRad) * dt
        T = Q / (m*c)+T
        #heaterOn = subprocess.check_output([sys.executable, decodedFile, str(T)])
        heaterOn = decoded.readTemp(T,heaterOn)
        if heaterOn:
            qHeater = 10 # Watts
        else:
            qHeater = 0.0
        i += 1
        if not i%60:
            sleep(0.1)
            print("Temp: %.2fC"%T,end='\r')
            sys.stdout.flush()
        #sleep(1)
        if T > 70:
            print("The spacecraft exceeded its operating temperature! You got it!")
            return 1
        if T < 0:
            print("The spacecraft exceeded its operating temperature! You got it!")
            return 1
    return 0

if __name__ == "__main__":
    # Challenge Intro
    render_intro()

    if os.path.exists(encodedFile):
        os.remove(encodedFile)
    if os.path.exists(decodedFile):
        os.remove(decodedFile)

    # Encode file
    file    = open(sensorFile, "rb")
    encFile = open(encodedFile, 'wb')
    
    data = bytearray(file.read(8))
    while data:
        encData = encode(data)
        encFile.write(encData)
        data = bytearray(file.read(8))

    file.close()
    encFile.close()

    # Allow teams to flip 3 bits
    # Change 0x3C to 0x3E to win...
    # 7020 3c20 3135 2061 d4
    # 7020 3e20 3135 2061 64
    # byte 161, bits 4,5,7
    #
    # 01110000 00100000 00111100 00100000 00110001 00110101 00100000 01100001 11010100
    #                         ^                                               ^ ^^                         
    # 01110000 00100000 00111110 00100000 00110001 00110101 00100000 01100001 01100100
    try:
        i = 0
        while i < 3:
            ionize(i+1)
            i += 1
    except TimeoutError:
        sys.stdout.write("\nTimeout, Bye\n")
        sys.exit(1)

    # 3 FLIPS EXAMPLE
    # TRUTH:    00011010 11001111 11111100 00011101 11111111 11111111 11111111 11111111 11011001
    #                          ^       ^       ^
    # FLIPPED:  00011010 11001101 11111000 00010101 11111111 11111111 11111111 11111111 11011001
    #                                                  ^
    # SECDED:   00011010 11001101 11111000 00010101 11101111 11111111 11111111 11111111 11011001

    # Decode file and error correct
    if os.path.exists(decodedFile):
        os.remove(decodedFile)

    encFile = open(encodedFile, "rb")
    decFile = open(decodedFile, 'wb')

    encData = bytearray(encFile.read(9))
    while encData:
        data = decode(encData)
        decFile.write(data)
        encData = bytearray(encFile.read(9))

    encFile.close()
    decFile.close()

    success = 0
    # Run file
    try: 
        import decoded
        success = simulate()
    except:
        print("Memory is corrupted. Aborting operation.")

    
    # If file has been modified correctly, provide flag
    if success:
        print("Here's your flag: ")
        flag = os.getenv('FLAG')
        print(flag)
    else:
        print("\nThat didn't work, try again!")
