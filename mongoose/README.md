# mongoose_mayhem

# The Challenge

Old fashioned exploitation using shellcode on a Mongoose (MIPS) processor to exfil the flag from memory

## Things they need in the S3 bucket

1) the vmips emulator binary
2) the firmware for the challenge

## Starting the challenge in Docker

docker run -e FLAG=<flag> mongoose_mayhem:challenge


## Solver Environment Variables

HOST: The hostname/IP address where the challenge is listening
PORT: The port number the challenge is bound to
TICKET: The ticket to pass to the Ticket Taker, if the challenge is being run that way

## Running the solver in Docker

Assuming the challenge is already running on host:port

docker run -e HOST=<host> -e PORT=<port> mongoose_mayhem:solver

