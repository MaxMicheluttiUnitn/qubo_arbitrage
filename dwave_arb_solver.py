import arbtoqubo_v2 as atq
import math
import numpy as np
import csv
import requests as req
import math
from os.path import exists
import dimod
import pandas
from dwave.system.composites import EmbeddingComposite
from dwave.system.samplers import DWaveSampler

def make_bqm_from_qubo_matrix(qubo):
    "this function translates the qubo matrix in a form readable for dimod.BinaryQuadraticModel"
    bqm={}
    for i in range(len(qubo)):
        for j in range(i,len(qubo)):
            bqm.update({(i,j):qubo[i][j]})
    return bqm

def convert_response_to_numpy(response):
    panda=response.to_pandas_dataframe(sample_column=True)
    array=panda.to_numpy()
    return array
            
def solve(qubo,sampler=None):
    "this function solves a qubo problem through the dwave sampler"
    bqm=make_bqm_from_qubo_matrix(qubo)
    if sampler == None:
        dwavesampler=DWaveSampler()
        print(dwavesampler.properties['topology'])
        sampler = EmbeddingComposite(dwavesampler)
    bqm = dimod.BinaryQuadraticModel.from_qubo(bqm)
    response = sampler.sample(bqm, num_reads=1000)
    return response
    #return [subsets[i] for i in sample if sample[i]]

def find_best_valid_solution(edges,table,vtc,ctv,see_error=False):
    sol=[]
    energy=0
    occurs=0
    for row in table:
        #if row[2]>1:
        for k in row[0].keys():
            sol.append(row[0][k])
        atq.make_solution_valid(sol)
        print(sol)
        if atq.check_arbitrage_solution_validity_weak_multiple_cycle(edges,sol,see_error):
            energy=row[1]
            occurs=row[2]
            return sol,energy,occurs
        sol=[]
    return None,0,0
        

def main():
    "main function for the dwave_arb_solver module"
    print("Getting Problem...")
    edg,valtocod,codtoval=atq.get_problem()
    #edg=atq.test_values()
    edg_small=atq.make_small(edg)
    #print(edg_small)
    print("Building QUBO...")
    qubo=atq.get_qubo(edg_small,20,20)
    print("Getting results...")
    res=solve(qubo)
    #print(res)
    print("Parsing results...")
    table=convert_response_to_numpy(res)
    print("Checking results...")
    sol,nrg,ocs=find_best_valid_solution(edg_small,table,valtocod,codtoval)
    if(sol!=None):
        print(sol)
        print(nrg)
        print(ocs)
        print(atq.natural_solution(edg_small,sol,valtocod,codtoval))
    #solution=solve(qubo)
    #print(solution)


if __name__ == '__main__':
    main()