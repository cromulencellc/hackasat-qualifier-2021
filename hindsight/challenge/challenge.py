from starGen import *
import numpy as np
import sys, os, traceback
from timeout import timeout, TimeoutError
from common import *
from scipy.optimize import linear_sum_assignment

time = int(os.getenv("TIMEOUT",30))
error = os.getenv("ERROR", 5)
required = int(os.getenv("REQUIRED",10))

def grade(guess, actual):
    correct = 0
    wrong   = 0
    guess = set(guess)
    for g in guess:
        if g in actual:
            correct += 1
        else :
            wrong += 1
    return (correct, wrong)

@timeout(time)
def makeTest(stars_xyz):
    try:
        viewable, view_indices, targetV = genQuestion(stars_xyz)
        for v in viewable:
            sys.stdout.write("%f,\t%f,\t%f\n" % (v[0], v[1], v[2]))
        sys.stdout.write("\n")

        #print(f"TargetV (debug): {str(targetV)}")
        #print(f"View indices (debug): {str(view_indices)}")
        #create_3d_scatter_graph(viewable)

        while True:
            sys.stdout.write("Index Guesses (Comma Delimited):\n")
            sys.stdout.flush()
            guess = sys.stdin.readline().strip()
            if len(guess) == 0: 
                return False
            guesses = guess.split(",")
            if len(guesses) < required:
                print("More stars please, try again! (%d required)" % required)
                continue 
            try:
                guess_indices = set(map(int, guesses))
            except ValueError:
                print("Non Integer Detected, try again")
                continue
            if len(guess_indices) < len(guesses):
                print("Tried to use duplicates huh....")
                continue 

            (correct, wrong) = grade(guess_indices, view_indices)
            if (wrong > error):
                print("Too many were incorrect, try again")
            elif (correct < required):
                print("Not enough were correct, try again")
            else:
                break
    except TimeoutError as e:
        raise e
    except Exception:
        traceback.print_exc()
        return False
    return True

def dumpStars(stars_xyz, f):
    for row in stars_xyz:
        f.write(",\t".join(map(lambda x: str(x), row)))
        f.write("\n")
    f.write("\n")

if __name__ == "__main__":
    seed = 8036002836425871957 # int(os.getenv("SEED", 2020))
    flag = os.getenv("FLAG", "FooBarFlag")
    TrialCount = os.getenv("TRIALS", 5)

    np.random.seed(seed % 0xFFFFFFFF)
    stars_xyz = genStars()

    filename = "catalog.txt"
    with open(filename, "w+") as f:
        dumpStars(stars_xyz, f)

    #create_3d_scatter_graph(stars_xyz)
    
    for ii in range(0,TrialCount):
        try:
            win = makeTest(stars_xyz)
        except TimeoutError:
            sys.stdout.write("Timeout, Bye\n")
            sys.exit(1)

        if not win:
            sys.stdout.write("Failed...\n")
            sys.exit(2)
        sys.stdout.write("%d Left...\n" % (TrialCount - ii -1))
        sys.stdout.flush()

    sys.stdout.write(flag)
    sys.stdout.write("\n")
    sys.stdout.flush()
    sys.exit(0)
