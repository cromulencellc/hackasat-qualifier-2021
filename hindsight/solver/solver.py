from scipy import signal
from scipy import misc
import numpy as np
from starSolve import *
import sys, os, socket, pickle

if __name__ == "__main__":
    Host = os.getenv("HOST", "172.17.0.1")
    Port = int(os.getenv("PORT", 1337))
    File = os.getenv("DIR") + os.sep + "catalog.txt"

    Ticket = os.getenv("TICKET", "")

    sys.stdout.write(f"Solver initializing with HOST:{Host} Port:{Port} File:{File} Ticket:{Ticket}")

    stars = []
    with open(File, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if len(line):
                stars.append(list(map(float, line.split(','))))

    if not os.path.exists("triangles.cached"):
        sys.stdout.write("Creating Catalog from file... ")
        sys.stdout.flush()

        stars = np.array(stars, dtype='float64')
        triangles, indexes = genCatalog(stars)
        sys.stdout.write("Created Triangles from catalog, dumping to pickle\n")
        sys.stdout.flush()
        pickle.dump(triangles, open("triangles.cached", "wb"))
        pickle.dump(indexes, open("indexes.cached", "wb"))
    else:
        sys.stdout.write("Loading Triangles from pickle\n")
        triangles = pickle.load(open("triangles.cached", "rb"))
        indexes = pickle.load(open("indexes.cached", "rb"))

    print(f"Triangle catalog length: {len(triangles)}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((Host, Port))
    fsock = sock.makefile('rw')

    print(f"Connected to challenge sock from solver")
    
    if len(Ticket):
        fsock.readline()
        fsock.write(Ticket + "\n")
        fsock.flush()
        print("Sent", Ticket)

    #fsock = open("viewable.txt", "r")

    while True:
        sys.stdout.write("Doing Challenge...\n")
        sys.stdout.flush()
        viewable = []
        while True:
            line = fsock.readline()
            line = line.strip()
            sys.stdout.write(line)
            if len(line):
                viewable.append(list(map(float, line.split(",\t")) ))
            else:
                break
        sys.stdout.write(f"Viewable list: {len(viewable)}")
        prompt = fsock.readline()
        viewable = np.array(viewable,dtype='float64')
        guesses = np.array(makeGuess(triangles,indexes,viewable, stars))
        
        guessxyz = np.asarray([stars[g] for g in guesses])
        median = np.median(guessxyz, axis=0)
        #print(f"Median of data: {median}")
        s = np.abs(guessxyz-median)
        #print(f"Deviation: {s}")
        std = np.median(s, axis=0)
        #print(f"Standard Deviation: {std}")
        usable = s<std*2 # within 2 standard deviations
        usable = list(map(lambda x: x[0] and x[1] and x[2], usable))
        #create_3d_scatter_graph(guessxyz)
        guessxyz = guessxyz[usable] # remove outliers
        mean = np.mean(guessxyz, axis=0)
        print(f"Mean vector of non-outlier points: {str(mean)}")

        # Find the angular distance from each entry in the catalog, and list the closest 5 to the center of the FOV
        distances = np.array([cosVecDiff(mean, x) for x in stars])
        distanceindexes = list(zip(distances, np.arange(0, len(stars)))) # value, index
        distanceindexes.sort(key=lambda x: x[0])
        distanceindexes = np.array(distanceindexes)
        print(distanceindexes[:15,1])
        g = [int(x) for x in distanceindexes[:15,1]]
        g.sort()

        print(",".join(list(map(str, g))))

        # Graph the indexes that we matched up
        # Select from the catalog the indexes
        #create_3d_scatter_graph([stars[x] for x in g])

        sys.stdout.flush()
        fsock.write(",".join(list(map(str, g))))
        fsock.write("\n")
        fsock.flush()
        result = fsock.readline()
        if result[:6] == "Failed":
            sys.stdout.write("Failed!\n")
            sys.stdout.flush()
            break
        else:
            sys.stdout.write("Success!\n")
            count = int(result.split(" ")[0])
            sys.stdout.write("%d Left...\n" % count)
            sys.stdout.flush()
            if count == 0:
                break
    flag = fsock.readline()
    print(flag)
