"""Problems are mounting- A cubesat has 6 solar sensors, one on each side of the satellite.
At any given time, the sun can be observed by a maximum of 3 sensors at a time. The combination 
of measurements from 3 sensors provides the Sun vector in the spacecraft coordinate system. 
The spacecraft coordinate system is a cartesian system with the origin at the center of the
satellite. The sun vector, in combination with other observations such as the Earth magnetic field
vector can be used to determine the full 3D 
attitude of the spacecraft.

During launch, the mounting angle of one of the sun sensors shifted and is no longer aligned 
with the spacecraft coordinate system's axis causing the sun vector determination to be wrong.
Determine which of the 6 sensors was shifted and find it's vector norm in order to
make corrections to the attitude determination. 

Flag - correct vector norm of the shifted solar sensor

"""

import numpy as np
import math as m
from challenge.Hidden_code import *

class Cart_Vector(object):
    #Helpful class for working with vectors
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def vector(self):
        return np.array([[self.x], [self.y], [self.z]])
    def mag(self):
        return (self.x**2 + self.y**2 +self.z**2)**0.5
    def unit(self):
        return self.vector()/self.mag()


#Step 1 Calculate the theoretical expected voltage from a 1 cm^2 solar sensor
#with 10% efficiency at a distance of 1 AU and a 10 ohm resistor as a voltmeter

Lsol = 3.83e26 #W joules/cm^2/s
R = 10 #ohm
A = 1 #cm^2
e = .10
AU = 1.496e13 #cm

P = e*Lsol*A**2/(4*m.pi*AU**2)
V0 = np.sqrt(P*R)   #Apply ohms law to get the voltage
print(f'V = {V0}')

#Step 2, To begin the sun sensor calibration you take an initial measurment, 
# #calculate the total induced voltage, 

vx,vy,vz = observed0()
v1 = Cart_Vector(vx, vy, vz)
V1 = v1.mag()

E = (V1-V0)/V0
print(f'Total V = {V1}')
print(f'Error V = {E}')

print(f'Sun vector is {v1.unit()}')

#Hmm that's strange, it's the wrong value and is outside the acceptible noise level. 
#You conclude that the mounting angle of one of the sensors may have changed due forces
#exerted on the satellite during launch
#To test your theory, you design a series of satellite rotations to find out which of the sensors is defective. 
#gyros placed in the space craft are oriented in such a way that the space craft makes rotations about the craft
#  coordinate axes
# provide Euler angles that would expose 1 of the other three sensors to the sun. 
#Euler angle convention we are using is x-y'z"

phi = 45.
theta = 300.
psi = 45.

R = Rotation(phi, theta, psi)
v2x, v2y, v2z = observed1(R)
v2 = Cart_Vector(v2x, v2y, v2z)
V2 = v2.mag()
E = (V2-V0)/V0

print(f'Total V2 = {V2}')
print(f'Error = {E}')
print(f'New sun vector is {v2.unit()}')

#Repeat until the total measured voltage is what you expect it to be. 

# Once you identify which sensor is tilted, 
# Rotate this vector back to the original orientation to find what the value of that component
#  should be.
RT = R.transpose()

v3 = RT*v2.vector()
x,y,z = v3.flat
v3 = Cart_Vector(x,y,z)
V3 = v3.mag()

E = (V3-V0)/V0

print(f'Total V3 = {V3}')
print(f'Error = {E}')
print(f'New sun vector should be {v3.unit()}')

#Ding, Ding, this is the correct sun vector for position 0.  
#Now that we know what the measurement should have been, find the rotation matrix of the sensor.  
#note with only one measurment, we can only measure the angle from the axis. 

#we now know the position of the sun in space craft coordinates
#need to identify the euler angles to define the rotation of the faulty sun sensor
#find the rotation Matrix required to rotate space craft so that +x is to the sun. 
#and take a measurement



#  add if statements to get positive or negative

xnorm = Cart_Vector(1,0,0) 
Rxsun = xnorm.vector() * v3.unit().T
xobserved = axis_observed(Rxsun, xnorm, v3)
thetax = np.arccos(xobserved[0]/V0)

ynorm = Cart_Vector(0,1,0)
Rysun = ynorm.vector() * v3.unit().T
yobserved = axis_observed(Rysun, ynorm, v3)
thetay = np.arccos(yobserved[0]/V0)

mynorm = Cart_Vector(0,-1,0)
mRysun = ynorm.vector() * v3.unit().T
myobserved = axis_observed(Rysun, ynorm, v3)
mthetay = np.arccos(yobserved[0]/V0)

znorm = Cart_Vector(0,0, 1)
Rzsun = znorm.vector() * v3.unit().T
zobserved = axis_observed(Rzsun, znorm, v3)

mznorm = Cart_Vector(0,0,-1)
mRzsun = mznorm.vector()*v3.unit().T
mzobserved = axis_observed(Rzsun, mznorm, v3)

thetaz = np.arccos(zobserved[0]/V0)

#Now that you know the angles from the primary axes, determine the normal vector of the tilted sensor
tiltx = np.cos(thetax)
tilty = np.cos(thetay)
tiltz = np.cos(thetaz)

tilt = Cart_Vector(tiltx,tilty,tiltz)
print("The normal vector of the tilt is ", tilt.vector()  )

check_correct(tilt)

#take a look at centroid from last year
