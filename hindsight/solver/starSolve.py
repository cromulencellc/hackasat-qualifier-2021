from scipy import signal
from scipy import misc
from scipy.spatial.transform import Rotation as R
from scipy.optimize import linear_sum_assignment as munkres
from collections import defaultdict
from common import *
import numpy as np

refV = np.array([0,0,1])
minAngle = 1 * (np.pi/180.)
maxAngle = 10 * (np.pi/180.)

##
# Calculates Perimeter, Area, Inertial Moment and Ratio of longest and shortest
# Majority of these parameters are unused
def makeTriangle(a, b, c):
    a_n = np.linalg.norm(a)
    b_n = np.linalg.norm(b)
    c_n = np.linalg.norm(c)
    P = a_n + b_n + c_n
    s = P/2
    A = np.sqrt(s*(s-a_n)*(s-b_n)*(s-c_n))
    I = A * (a_n**2 + b_n**2 + c_n**2)/36
    tmp = [a_n, b_n,c_n]
    tmp.sort()
    s,m,l = tmp
    R = s/l
    return [I,R,A]

##
# Create a catalog of triangles of stars, with a metric that lets them be easily sortable
# [star1xyz, star2xyz, star3xyz, metric]
def genCatalog(stars_xyz):
    triangles,indexes = findTriangles(stars_xyz)

    together = list(zip(triangles, indexes))
    together.sort(key=lambda x: x[0][0])
    triangles, indexes = zip(*together)
    triangles = np.array(triangles)
    indexes = list(indexes)

    return np.asarray(triangles), np.asarray(indexes)

def findTriangles(stars_xyz):
    stars_xyz = np.array(stars_xyz)
    star_count = len(stars_xyz)

    triangles  = []
    indexes    = []

    for idx_ii in range(0,star_count-2):
        v_ii = stars_xyz[idx_ii]

        # Find all stars close enough to the first star
        pairs = []
        for jj in range(idx_ii+1,star_count):
            angle = cosVecDiff(v_ii, stars_xyz[jj])
            #print(f"[{idx_ii}]:{v_ii} [{jj}]:{stars_xyz[jj]}")
            #print(f"Angle calculated:{angle} maxAngle:{maxAngle} minAngle:{minAngle}")
            if angle < maxAngle and angle > minAngle:
                pairs.append(jj)
        #print(f"Pairs: {str(pairs)}")

        # Find 2 pairs that can form a triangle
        numPairs = len(pairs)
        for jj in range(0,numPairs-1):
            idx_jj = pairs[jj]
            v_jj = stars_xyz[idx_jj]
            for kk in range(jj+1,numPairs):
                idx_kk = pairs[kk]
                v_kk = stars_xyz[idx_kk]
                
                # Filter Oblique Triangles (last angle)
                angle = cosVecDiff(v_jj,v_kk)
                if angle < minAngle or angle > maxAngle:
                    continue

                a = v_jj - v_ii
                b = v_kk - v_ii
                c = a - b

                triangles.append(makeTriangle(a,b,c))
                idxs = [idx_ii, idx_jj, idx_kk]
                indexes.append(idxs)

    triangles = np.asarray(triangles)
    indexes = np.asarray(indexes)
    #print(f"findTriangles output: {str(triangles)}")
    return triangles, indexes

def findPotentials(triangles, indexes, vtriangles, vindexes, stars):
    stride = 200
    candidates = 5
    matches = defaultdict(list)
    potentials = set()

    for vidx in range(len(vtriangles)): # For every visible triangle:
        vt = vtriangles[vidx]
        idx = binarySearch(triangles[:,0], vt[0])[0]
        idxs = findBest(triangles[max(0,idx-stride):min(len(triangles),idx+stride)],
                        vt,
                        lambda a,b: -np.linalg.norm(np.subtract(a,b)),
                        n=candidates, base=max(0,idx-stride))
        # Find the entries that matches the metric best

        #for ii in range(3):
        #    matches[vindexes[vidx][ii]].append(indexes[idx][ii]) # Append possible catalog indexes
        #    potentials.add(indexes[idx][ii]) # Append all possible potentials

        for idx in idxs: # Compile a huge list of candidates
            if idx > len(indexes)-1:
                continue
            for ii in range(3):
                matches[vindexes[vidx][ii]].append(indexes[idx][ii]) # Append possible catalog indexes
                potentials.add(indexes[idx][ii]) # Append all possible potentials

    #print("Graphing potentials...")
    #create_3d_scatter_graph([stars[g] for g in potentials])

    potentials = list(potentials)
    potentials.sort()
    print(f"length of potentials: {len(potentials)}")
    return potentials, matches

def hungarian(potentials, matches):
    matchLen = len(matches.keys())
    costDim = max(matchLen,len(potentials))
    costA   = np.zeros((costDim, costDim))
    
    for vidx in range(matchLen):
        for pidx in range(len(potentials)):
            count = matches[vidx].count(potentials[pidx])
            if count > 0:
                costA[vidx,pidx] = (-1.0*count)/len(matches[vidx])

    print("Doing linear sum assignment...")
    row_idx, col_idx = munkres(costA)
    pairs = list(zip(row_idx, col_idx))[:matchLen]
    return pairs, costA

def makeGuess(triangles, indexes, viewable, stars):
    vtriangles, vindexes = findTriangles(viewable)
    #print("Starting to guess, calculated vtriangles:")
    #print(vtriangles)

    potentials, matches = findPotentials(triangles, indexes, vtriangles, vindexes, stars)
    
    # Find the indexes of stars that would best fill the slots
    pairs, costA = hungarian(potentials, matches)

    pairs.sort(key=lambda x:costA[x])
    
    indexes = list(map(lambda x: potentials[x[1]], pairs))

    return indexes

