import arbtoqubo_v2 as atq
import math
import numpy as np
import csv
import requests as req
import math
from os.path import exists
from dimod import BinaryQuadraticModel
from dwave.system import LeapHybridSampler



def solve(qubo,sampler=None):
    if sampler is None:
        sampler = LeapHybridSampler()

    sampleset = sampler.sample(qubo, label='First try - Arbitrage')
    print(sampleset)

    #return [subsets[i] for i in sample if sample[i]]

def main():
    #edg=atq.get_problem()
    edg=atq.test_values()
    edg_small=atq.make_small(edg)
    qubo=atq.get_qubo(edg_small,10,10)
    solution=solve(qubo)
    print(solution)


if __name__ == '__main__':
    main()