#problems are mounting hodden code
###final thing to fix is the initializing the random seeds
#or make them globals.
import numpy as np
import math as m
import random
from challenge import out, log


#Globals
sunseed = np.random.randint(1000)
angleseed = np.random.randint(1000)
tiltid = np.random.randint(3)



def init_random(seed):

    random.seed(seed)
    x = random.random()
    y = random.random()
    z = random.random()

    return x, y, z

# write a python class to define vectors. include a function to calculate vector magnitude.
# probably going to change this class to be a little more intuitive.  maybe just define a mag, and unit functions
# without invoking a class.  Need to think about the team would solve this problem. 
class Cart_Vector(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def vector(self):
        return np.array([[self.x], [self.y], [self.z]])
    def mag(self):
        return np.sqrt(self.x**2 + self.y**2 +self.z**2)
    def unit(self):
        return self.vector()/self.mag()


def Rx(theta):
  return np.matrix([[ 1, 0           , 0           ],
                   [ 0, m.cos(theta),-m.sin(theta)],
                   [ 0, m.sin(theta), m.cos(theta)]])
  
def Ry(theta):
  return np.matrix([[ m.cos(theta), 0, m.sin(theta)],
                   [ 0           , 1, 0           ],
                   [-m.sin(theta), 0, m.cos(theta)]])
  
def Rz(theta):
  return np.matrix([[ m.cos(theta), -m.sin(theta), 0 ],
                   [ m.sin(theta), m.cos(theta) , 0 ],
                   [ 0           , 0            , 1 ]])



def Rotation(phi,theta,psi):
    phi = m.radians(phi)
    theta = m.radians(theta)
    psi = m.radians(psi)
    return Rx(phi) * Ry(theta) * Rz(psi)

def get_tilt_norm(axis, angleseed):
    #the normal of the tilted sensor
    
    x,y,z = init_random(angleseed)
    x,y,z = Cart_Vector(x,y,z).unit().flatten()
    #print('angle', vector_angle(axis, tiltnormB))
    #log(f'+correct tiltnorm {tiltnormB.vector()}')   
    return Cart_Vector(x,y,z)

def get_V0():
    Lsol = 3.83e26 #W
    R = 10 #ohm
    A = 1
    e = .10
    AU = 1.496e13 #cm

    P = e*Lsol*A**2/(4*m.pi*AU**2) #Solar constant times 10%
    V0 = np.sqrt(P*R)   #Apply ohms law to get the voltage
    return V0

def vector_angle(v1, v2):
    Costheta = np.dot(v1.vector().flatten(), v2.vector().flatten())/(v1.mag()*v2.mag())
    if Costheta < 0:
        return m.pi - np.arccos(-1*Costheta)
    else:
        return np.arccos(Costheta)

def SunV():
    V0 = get_V0()
    
    x, y, z = init_random(sunseed)
    SunV = V0 * 1/np.sqrt(x**2+y**2+z**2) * np.array([[x],
        [y],
        [z]])

    x,y,z = SunV.flatten()
       
    return Cart_Vector(x,y,z)

def correct_angle(angleseed):
    
    a,b,c = init_random(angleseed)
    phi =  a * 70     
    theta = b * 70
    psi = c * 70
    return phi, theta, psi

def tilt_sensor_id():
    id = np.zeros(3)
    id[tiltid] = 1
    #print(id)
    return  id

def observed0():
    # angleseed
    global angleseed
    E=0
    while E < 0.05:
        angleseed = angleseed+1
        #phi, theta, psi = correct_angle(angleseed)
        #tilted sensor axis
        x,y,z = tilt_sensor_id()
        id = Cart_Vector(x,y,z)
        tiltnormB = get_tilt_norm(id, angleseed)
        CorrectSunV = SunV()
        V0 = get_V0()
        #angle between the tilted sensor and the SunV
        thetax = vector_angle(tiltnormB, CorrectSunV)
        observed1 = V0*np.cos(thetax)

        observed = CorrectSunV.vector()
        i = np.argmax(id.vector())
        observed[i] = [observed1]
        x,y,z = observed.flatten()
        v1 = Cart_Vector(x,y,z)

        V1 = v1.mag()

        E = abs((V1-V0)/V0)
        
    O = [max(0,x), max(0,y), max(0,z), max(0,-x), max(0, -y), max(0,-z)]
    return O

def observed1(R):

    norm = tilt_sensor_id()
    i = np.argmax(norm)
    #print("+++bad sensor", i)
    CorrectSunV = SunV()
    v2true = R*CorrectSunV.vector()
    x,y,z = v2true.flat
    O = [max(0,x), max(0,y), max(0,z), max(0,-x), max(0,-y), max(0,-z)]
    V0 = get_V0()
    #phi, theta, psi = correct_angle(angleseed)
        #tilted sensor axis
    xx,yy,zz = tilt_sensor_id()
    id = Cart_Vector(xx,yy,zz)

    tiltnormB = get_tilt_norm(id, angleseed)
    v2truee = Cart_Vector(x,y,z)
    thetax = vector_angle(tiltnormB, v2truee)
    #print(tiltnormB)
    #print(thetax)
    observed1 = V0*np.cos(thetax)
    #log(f"++observed {observed1}")
    if observed1 > 0:
        O[i] = observed1
    else:
        O[i] = 0
    return O
   
def axis_observed(Rsun,norm,vector):
    V0 = get_V0()
    measured = np.mat(Rsun)*vector.vector()
    phi, theta, psi = correct_angle(angleseed)
    x,y,z = tilt_sensor_id()
    id = Cart_Vector(x,y,z)  
    tiltnormB = get_tilt_norm(id, phi, theta, psi)
    theta = vector_angle(tiltnormB, norm)
    x = V0*np.cos(theta)
    if x < 0:
        x = 0    
    measured[np.argmax(id.vector())] = x
    return measured

def check_correct(tilt):
    #phi, theta, psi = correct_angle(angleseed)
    #tilted sensor axis
    x, y, z,= tilt_sensor_id()  
    norm = Cart_Vector(x,y,z)  #can be ony of the 6
    tiltnormB = get_tilt_norm(norm, angleseed)
    tiltnormB = tiltnormB.vector()
    Correct=[]
    for i, t in enumerate(tilt.vector()):
        try:
            E = abs((t-tiltnormB[i])/tiltnormB[i])
            if E > .05:
                out(f'Error = {E}, component {i} incorrect, try again.  \n')
                Correct.append(0)
            else:
                out(f'Error = {E}, component {i} is correct \n')
                Correct.append(1)
        except:
            out(f"Component {i} should be a real number....\n")
            out("Try again \n")
            Correct.append(0)
    log(f"Should be {tiltnormB.flatten()} \n ")   
    log(f"tilted axis should be {norm.vector()} \n")
    if all(Correct):
        return True
    
    else:
        return False
