# mars_or_bust

# The Challenge

The challenge is a nodejs application that runs a simulation of the vertical landing
velocity of a spacecraft headed for Mars. The challenge idea is based on the failed
landing attempt of the Mars Polar Lander in 1999. The most likely failure of that lander
was a bug in the controller software that ultimately resulted in premature shutdown of 
the descent engines. For the simulation, the controller software is running inside the 
VMIPS emulator which is invoked by the nodejs application. Communication in and out of
the controller is through stdin/stdout that are mapped to UARTs inside the emulator.

The goal of the challenge is to determine the problem with the controller by running 
the simulator and reverse engineering the ROM image, and then applying a patch to the 
ROM to fix the error.  The competitor obtains the flag by uploading the patched ROM and
re-running the simulation to a successful landing, i.e. touching down at less than 
2.6 m/s, landing gear extended, and thrusters shutdown within 200ms of landing. 

The challenge uses TCP sockets to provide a webUI interface via HTML and websockets, 
and thus requires the use of Life Cycle Manager (LCM) to be deployed in the game
infrastructure. The webUI allows the competitors to run the simulation, download a copy
of the baseline ROM image, and upload a new ROM image.  Upon a successful simulation,
it presents the flag.

## Environment variables:

PORT: the TCP port to bind the webserver to on startup.  Pointing a browser at this port
retrieves the webUI.

FLAG: the flag data.

## Starting the challenge in Docker

docker run -e PORT=<port#> -e FLAG=<flag> -p <port#:port#> mars:challenge

# Solver

The solver is a Python app that uses the websocket module to perform the same actions
a competitor is expected to do:

1) Retrieve the baseline ROM
2) Patch the ROM
3) Upload the ROM
4) Run a simulation
5) Wait for the flag at the end of the simulation

## Solver Environment Variables

HOST: The hostname/IP address where the challenge is listening
PORT: The port number the challenge is bound to

## Running the solver in Docker

Assuming the challenge is already running on host:port

docker run -e HOST=<host> -e PORT=<port> mars:solver

