# Quals Challenge: Linky #

**Category:** Guardians of the...
**Relative Difficulty:** 1/5
**Author:** [Cromulence](https://cromulence.com/)

Years have passed since our satellite was designed, and the Systems Engineers didn't do a great job with the documentation. Partial information was left behind in the user documentation and we don't know what power level we should configure the Telemetry transmitter to ensure we have 10 dB of Eb/No margin over the minimum required for BER (4.4 dB)
```
 _     _       _
| |   (_)_ __ | | ___   _ 
| |   | | '_ \| |/ / | | |
| |___| | | | |   <| |_| |
|_____|_|_| |_|_|\_\\__, |
                    |___/
    .-.
   (;;;)
    \_|
      \ _.--l--._
     . \    |     `.
   .` `.\   |    .` `.
 .`     `\  |  .`     `.
/ __      \.|.`      __ \/
|   ''--._ \V  _.--''   |
|        _ (\") _        |
| __..--'   ^   '--..__ | 
\         .`|`.         /-.)
 `.     .`  |  `.     .`
   `. .`    |    `. .`
     `._    |    _.`|
         `--l--`  | |
                  | |
                  | |
                  | |
         o        | |     o
          )    o  | |    (
         \|/  (   | |   \|/
             \|/  | | o  WWwwwW
                o | |  )  
               \|/WWwwWWwW
```

## Solution Notes ##
### Step 1 - Solve for the Ground Terminal Antenna Gain based on the provided Antenna Diameter and Efficiency

### Step 2 - Calculate the Ground Terminal G/T based on the calculated gain, provided System Noise Temperature, and Antenna to LNA line losses

### Step 3 - Calculate the transmit power in watts to achive 10 dB of link margin (above minimum for BER)
This step requires that you perform a number of calculations to arrive at the required transmitted power.

```
The solver goes in the following order:
Calculates required S/No
Calculates required rssi (at the ground terminal)
Calculates required EIRP (at the S/C)
Calculates Pt at the Telemetry Transmitter
```