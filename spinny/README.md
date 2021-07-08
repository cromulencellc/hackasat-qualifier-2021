# Quals Challenge: Saving Spinny #

**Category:** Guardins of the ...
**Relative Difficulty:** 4/5
**Author:** [Cromulence](https://cromulence.com/)

We've lost control of our spacecraft, Spinny, and it no longer points its directional antenna at our ground stations. You'll need to account for the spacecraft spin rates, as well as its orbit to upload the correct command sequence from ground stations around the world. In order to stop spinning, you'll need to send the following commands in the correct order:
```
CMD1: "PLEASE"
CMD2: "STOP"
CMD3: "SPINNING!"
```

Due to Spinny's limited radio capabilities, it requires contact windows of at least 3 minutes and can only receive one word at a time. The spacecraft antenna must be pointed within 45 degrees of a ground station to receive. Since you cannot point the spacececraft, you will have to predict when it will be pointed at a ground station based on a known initial pointing vector and constant body spin rates.
```
Constant spacecraft body spin rate of [0.1,0.1,0.1] rad/s in XYZ
Initial spacecraft antenna pointing direction of [1,0,0] in the J2000 frame at the TLE epoch (2021-06-26 00:00:00 UTC)
```

Commands are queued at ground stations using the following format:
```
SYNTAX: YYYY-MM-DD-hh:mm:ss-UTC STATION CMD SAT CMD_WORD
EXAMPLES:
2021-06-26-01:00:00-UTC BANGALOR CMD SPINNY PLEASE
2021-06-26-02:00:00-UTC GRIMSTAD CMD SPINNY STOP
2021-06-26-03:00:00-UTC SVALBARD CMD SPINNY SPINNING!
```

Spinny's TLE is:
```
Spinny
1 75001F 21750A   21177.00000000  .00000000  00000-0  00000-0 0   51
2 75001  98.0875 274.0660 0000000   0.0000 359.9920 14.57890000 1100
```

Ground stations are located at (WGS-84):
| Name | Latitude (deg) | Longitude (deg) | Altitude (m) |
|------|-----------|-----------|---------------|
| BANGALOR | 13.0344 | 77.5116 | 823 |
| GRIMSTAD | 58.33 | 8.35 | 211 |
| SVALBARD | 78.2307 | 15.3897 | 497 |
| TROLLSAT | -72.0117 | 2.53838 | 1400 |
| TROMSO | 69.6625 | 18.9408 | 134 |


Correctly queue commands at the ground stations over 12 hours to rescue Spinny and get the flag.

## Running Challenge ##
Create and run the challenge container `spinny:challenge`
```sh
make challenge
nc localhost 12345
```

## Running Solver ##
Create and run the solver container `spinny:solver` against the challenge container `spinny:challenge`
```sh
make solver
```
