from scipy import signal
from scipy import misc
import numpy as np

from common import *

Bright_Step = 10
Bright_Base = 500
NumNearby = 3

refV = np.array([0,0,1])
FOV = 30

##
# Stars are supposed to be randomly distributed, and then a subset of stars should be selected
# when creating a catalog. This requires a huge number of stars and participants would have to 
# spend a lot of time picking stars. Instead, let's be more generate stars to ensure every possible
# view angle has at least some "good" triangles to make a catalog around. Stars are organized by 
# Magnitude, and represented by (x,y,z, mag)
#
# By putting bright approximately evenly distributed around a sphere, and adding some nearby stars 
# around them we'll ensure every field of view has some possible triangles. We'll then just fill
# in the rest of the stars randomly to pad out the quantity.
def genStars():
    brights = []
    nearby = []
    numBrights = 0
    # Steps through the declination angle, fixed step size
    for theta in range(-90,90,Bright_Step):
        # Steps through the ascension angle, step size varies based on declination to more
        # evenly distribute points
        r = np.sqrt(1 - np.sin(theta*np.pi/180.)**2) + 0.00001
        step = max(1,int(Bright_Step/r))
        for phi in range(0,360,step):
            # Bright Star [angle, angle, mag], without noise
            b = [theta*(np.pi/180.), phi*(np.pi/180.),Bright_Base]
            brights.append(b)
            
            # Generate Nearby Stars, ensuring they are not too close, and not too far
            # Do a simple hack to transform the uniform random output to +/-(1 + rand)
            for ii in range(NumNearby):
                n =  np.random.rand(3)
                if n[0] > 0.5:
                    n[0] = -(n[0]-0.5)
                if n[1] > 0.5:
                    n[1] = -(n[1]-0.5)
                n = b * np.array([1,1,0]) + 2*n * np.array([5*np.pi/180., 5*np.pi/180., Bright_Base/10.])
                n[2] += Bright_Base/5.
                nearby.append(n)

    
    # Apply noise to brights
    noise = np.random.rand(len(brights),3) * np.array([[ 5*np.pi/180.,
                                                         5*np.pi/180.,
                                                         Bright_Base/10. ]])
    brights += noise

    brights = np.array(brights)
    nearby = np.array(nearby) 

    numBrights = len(brights)
    numNearby  = len(nearby)

    #numDims = max(0, NumStars - numBrights - numNearby)
    #dims = np.random.rand(numDims,3) # N x Theta, Phi
    #dims = dims * np.array([[np.pi, 2*np.pi, Bright_Base/5.]]) 
    #dims += np.ones((numDims, 3)) * np.array([[-np.pi/2,0,Bright_Base/10.]])

    stars = np.concatenate((brights, nearby), axis=0)
    stars = stars[stars[:,2].argsort()[::-1]]
    stars_xyzm = star_anglesToCart(stars)
    return np.asarray(stars_xyzm)[:,:3] # clip off the magnitude

##
# Takes a target view angle, and returns all viewable vectors (in catalog ref frame)
# and the corresponding indexes into the list of stars
def selectViewable(stars_xyz, target):
    stars_xyz = np.array(stars_xyz)
    viewable = []
    viewable_idx = []
    star_count = len(stars_xyz)
    angle_limit = FOV/2. * np.pi/180.
    for star_idx in range(star_count):
        star = stars_xyz[star_idx,:]
        angle = cosVecDiff(target, star)
        if angle < angle_limit:
            viewable.append(star) 
            viewable_idx.append(star_idx)

    return np.array(viewable), viewable_idx

##
# Generate a random viewpoint and rotation and return all viewable vectors (in the viewpoint 
# reference frame), as well as the solution indexes
def genQuestion(stars_xyz):
    quat = normalizeV(np.random.rand(4))
    targetV = rotateByQuat(quat, np.array([0,0,1]))
    #print(f"targetV:{str(targetV)}")
    viewable, viewable_idx = selectViewable(stars_xyz, targetV)

    # Normal distribution noise, scale is standard deviation
    noise = np.random.normal(scale=.0005,size=viewable.shape) # Normal distribution noise
    #noise = np.random.rand(*viewable.shape)*.01 # rectangular noise
    viewable += noise

    viewable = rotateByQuat([-quat[0], -quat[1], -quat[2], quat[3]], viewable)
    viewable = viewable/np.linalg.norm(viewable, axis=1, keepdims=True)
    #create_3d_scatter_graph(viewable)
    return viewable, viewable_idx, quat
