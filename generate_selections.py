
from selection import *
import sys
import pickle
from random import Random

args = sys.argv[1:]

N = int(args[0])
L = int(args[1])
R = Random()
infileName = args[2]
outfileName = args[3]

if infileName == '-':
    coll = set()
else:
    coll = pickle.load(open(infileName, "rb"))

generate_selections(R, N, L, coll)

pickle.dump(coll, open(outfileName, "wb"))

