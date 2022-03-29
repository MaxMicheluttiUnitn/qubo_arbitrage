import numpy as np
import arbtoqubo_v2 as atq
import math

def arbitrage_classic_solver(edges):
    "this function wraps another function that tests all possible solutions to find the best one"
    solution=[]
    best_value=[0]
    last_solution=np.zeros(shape=(len(edges)),dtype=int) #choosing nothing which gains 0 is chosen as the basic solution, greedy choices could improve this algorithm
    test_all(edges,0,solution,last_solution,best_value)
    return last_solution

def arbitrage_to_qubo_classic_solver(qubo):
    solution=[]
    best_value=[1000000]
    last_solution=np.zeros(shape=(len(qubo)),dtype=int)
    qubo_test_all(qubo,0,solution,last_solution,best_value)
    return last_solution

def qubo_test_all(qubo,index,solution,last_solution,best_result):
    if index==len(qubo):#accept
        qubo_process_solution(qubo,solution,last_solution,best_result)
    else:
        if qubo_reject(qubo,index,solution):#reject
            return
        else:
            solcopy=solution[:]
            solcopy.append(False)
            qubo_test_all(qubo,index+1,solcopy,last_solution,best_result)
            solcopy=solution[:]
            solcopy.append(True)
            qubo_test_all(qubo,index+1,solcopy,last_solution,best_result)

def qubo_reject(qubo,index,solution):
    return False

def qubo_process_solution(qubo,solution,last_solution,best_result):
    value=atq.compute_solution_value(solution,qubo)
    if value<best_result[0]:
        best_result[0]=value
        for i in range(len(solution)):
            last_solution[i]=solution[i]




def arbitrage_cycle_multiplier_calc(edges,solution):
    sum=0
    for i in range(len(solution)):
        if solution[i]:
            sum+=edges[i][2]
    return sum




def process_solution(edges,solution,last_solution,best_value):
    "this function checks if a solution is valid and evaluates the solution"
    #validity checking
    #check cycle possibility
    nodes={}
    edge_taken=[]
    for i in range(len(edges)):
        if solution[i]:
            if edges[i][0] in nodes.keys():
                nodes[edges[i][0]]+=1
            else:
                nodes.update({edges[i][0]:1})
            if edges[i][1] in nodes.keys():
                nodes[edges[i][1]]+=1
            else:
                nodes.update({edges[i][1]:1})
            edge_taken.append(edges[i])
    if len(edge_taken)<2:
        return
    for j in nodes.values():
        if j!=0 and j!=2:#if there is a node with an odd number of edges in the solution, the solution is invalid
            return
    #check if cycle
    #length=0
    cycle=[edge_taken[0]]
    while cycle[0][0]!=cycle[-1][1]:
        found=False
        for e in edge_taken:
            if e[0]==cycle[-1][1]:
                cycle.append(e)
                found=True
                break
        if not found:#if it is impossible to finish the cycle the solution is invalid
            return
    if len(cycle)<len(edge_taken):#if some edges are not in the cycle the solution is invalid
        return
    #evaluation
    sum=0
    for i in range(len(solution)):
        if solution[i]:
            sum+=edges[i][2]
    #comparing with best_value
    if sum>best_value[0]:
        for i in range(len(solution)):
            last_solution[i]=solution[i]
        best_value[0]=sum
    #print(sum)



def reject(edges,index,solution):
    "this function checks if a partial solution is invalid"
    #if there are more then 2 edges entering or exiting the same node the solution is invalid
    nodes={}
    for i in range(index):
        if solution[i]:
            if edges[i][0] in nodes.keys():
                nodes[edges[i][0]]+=1
                if nodes[edges[i][0]]>2:
                    return True
            else:
                nodes.update({edges[i][0]:1})
            if edges[i][1] in nodes.keys():
                nodes[edges[i][1]]+=1
            else:
                nodes.update({edges[i][1]:1})
                if nodes[edges[i][1]]>2:
                    return True
    return False



def test_all(edges,index,solution,last_solution,best_result):
    "this function tests all possible solutions to find the best one"
    if index==len(edges):#accept
        process_solution(edges,solution,last_solution,best_result)
    else:
        if reject(edges,index,solution):#reject
            return
        else:
            solcopy=solution[:]
            solcopy.append(False)
            test_all(edges,index+1,solcopy,last_solution,best_result)
            solcopy=solution[:]
            solcopy.append(True)
            test_all(edges,index+1,solcopy,last_solution,best_result)


def main():
    #edg=atq.get_problem()
    edg=atq.test_values()
    #print(mat,"\n")
    #print(edg,"\n")
    edg_small=atq.make_small(edg)
    qubo=atq.get_qubo(edg_small,10,10)
    print("Qubo is:\n",qubo,"\n")
    #print("Edge Matrix is:\n",mat_small,"\n")
    print("Edges are:\n",edg_small,"\n")
    #mat_small_log=atq.logarithm_on_all(mat_small)
    solution=arbitrage_classic_solver(edg_small)
    qubo_solution=arbitrage_to_qubo_classic_solver(qubo)
    print(solution)
    print(qubo_solution)
    sum=arbitrage_cycle_multiplier_calc(edg_small,solution)
    qubo_sum=arbitrage_cycle_multiplier_calc(edg_small,qubo_solution)
    print(sum," ",2.0**sum)
    print(qubo_sum," ",2.0**qubo_sum)

if __name__ == '__main__':
    main()