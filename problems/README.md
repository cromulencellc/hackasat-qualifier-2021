# Quals Challenge: Problems Are Mounting #

**Category:** Deck 36, Main Engineering
**Relative Difficulty:** 2/5
**Author:** [Cromulence](https://cromulence.com/)

A cubesat has 6 solar sensors, one on each side of the satellite. At any given time, the sun can be observed by a maximum of 3 sensors at a time. The combination 
of measurements from 3 sensors provides the sun vector in the spacecraft coordinate system. 

The spacecraft coordinate system is a cartesian system with the origin at the center of the satellite. The sun vector, in combination with other observations such as the Earth magnetic field vector can be used to determine the full 3D attitude of the spacecraft.

During launch, the mounting angle of one of the sun sensors shifted and is no longer aligned with the spacecraft coordinate system's axis causing the sun vector determination to be wrong.

Determine which of the 6 sensors was shifted and find it's vector norm in order to make corrections to the attitude determination. To get the flag, find the correct vector norm of the shifted solar sensor.

Given information:
6 solar sensors on a cubesat, one on each face. In spaceecraft coodinates the vector norms should be (1,0,0), (0,1,0), (0,0,1), (-1,0,0), (0,-1,0), (0,0,-1).

One of the sensors shifted and is no longer aligned with the axis of the satellite.

Assume the satellite is always 1 A.U. (Astronomical Unit distance from the sun).
Each solar sensor has a 1 square cm area and a 10% efficiency. A 10 ohm resistor is used as a voltmeter.

## Building ##
Builds the challenge and solver containers `problemsmounting:challenge` and `problemsmounting:solver`
```sh
make build
```

## Testing ##
Test the solver container `problemsmounting:solver` against the challenge container `problemsmounting:challenge`
```sh
make test
```

## Solution Notes ##
problemsmounting.py is the solution to the problem

Hidden_code.py is how the sun "observations" are calculated and should be hidden from the contestants somehow.    

Solution steps

#Step 1 Calculate the theoretical expected voltage from a 1 cm^2 solar sensor
#with 10% efficiency at a distance of 1 AU and a 10 ohm resistor as a voltmeter.

#Step 2, To begin the sun sensor calibration you take an initial measurment and 
#calculate the total induced voltage

    -They measure the wrong value

#Hmm that's strange, it's the wrong value and is outside the acceptible noise level. 
#You conclude that the mounting angle of one of the sensors may have changed due forces
#exerted on the satellite during launch

Step 3
#To test your theory, you design a series of satellite rotations to find out which of the sensors is defective. 
#gyros placed in the space craft are oriented in such a way that the space craft makes rotations about the craft coordinate axes.
#Hint-provide Euler angles that would expose 1 of the other three sensors to the sun. 
#Euler angle convention we are using is x-y'z"

#Repeat until the total measured voltage is what you expect it to be. This will allow you to identify which of the sensors is tilted.

Step 4
#Once you identify which sensor is tilted, 
#Rotate back to the original orientation to find what the value of that component
#should be. 

#Ding, Ding, this is the correct sun vector for position 0.  
#Now that we know what the measurement should have been, find the rotation matrix of the sensor.  
#note with only one measurment, we can only measure the angle from the axis. 

step 5
#we now know the position of the sun in space craft coordinates
#need to identify the euler angles to define the rotation of the faulty sun sensor
#find the rotation Matrix required to rotate space craft so that side of the spacecraft with the tilted sensor is to the sun and take a measurement. Calculate the angle away from normal of the sun.

V=V0cos(theta)

repeat for the other two normal directions. 

step 6
#Now that you know the angles from the primary axes, determine the normal vector of the tilted sensor

check_correct is a function that will give the flag if it's correct.
