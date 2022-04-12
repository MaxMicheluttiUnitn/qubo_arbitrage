import numpy as np
import arbtoqubo_v2 as atq
import math
import classical_min_cycle_in_graph as min_cycle

def arbitrage_classic_solver(edges):
    "this function wraps another function that tests all possible solutions of the classical arbitrage problem to find the best one"
    solution=[]
    best_value=[0]
    last_solution=np.zeros(shape=(len(edges)),dtype=int) #choosing nothing which gains 0 is chosen as the basic solution, greedy choices could improve this algorithm
    test_all(edges,0,solution,last_solution,best_value)
    return last_solution

def arbitrage_to_qubo_classic_solver(qubo):
    "this function wraps another function that tests all possible solutions of the qubo problem to find the best one"
    solution=[]
    best_value=[1000000]
    last_solution=np.zeros(shape=(len(qubo)),dtype=int)
    qubo_test_all(qubo,0,solution,last_solution,best_value)
    return last_solution

def qubo_test_all(qubo,index,solution,last_solution,best_result):
    "this function tests all possible boolean vectors to solve the qubo problem"
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
    "this function processes the solution of the qubo problem"
    value=atq.compute_solution_value(solution,qubo)
    if value<best_result[0]:
        best_result[0]=value
        for i in range(len(solution)):
            last_solution[i]=solution[i]









def process_solution(edges,solution,last_solution,best_value):
    "this function checks if a solution is valid and evaluates the solution"
    #validity checking
    #check cycle possibility
    if not atq.check_arbitrage_solution_validity(edges,solution):
        return
    #evaluation
    sum=atq.arbitrage_cycle_multiplier_calc(edges,solution)
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
            solcopy.append(0)
            solcopy.append(0)
            test_all(edges,index+2,solcopy,last_solution,best_result)
            solcopy=solution[:]
            solcopy.append(0)
            solcopy.append(1)
            test_all(edges,index+2,solcopy,last_solution,best_result)
            solcopy=solution[:]
            solcopy.append(1)
            solcopy.append(0)
            test_all(edges,index+2,solcopy,last_solution,best_result)


def translate_in_mingraph(edges):
    "deprecated, do not use"
    node_ids=dict()
    id_to_node=dict()
    for e in edges:
        if not (e[0] in node_ids.keys()):
            node_ids.update({e[0]:len(node_ids)})
            id_to_node.update({node_ids[len(node_ids)-1]:e[0]})
        if not (e[1] in node_ids.keys()):
            node_ids.update({e[1]:len(node_ids)})
            id_to_node.update({node_ids[len(node_ids)-1]:e[1]})
    edg_new=edges[:]
    for e in edg_new:
        e[0]=node_ids[e[0]]
        e[1]=node_ids[e[1]]
        e[2]=100-e[2]
    graph=min_cycle.Graph(len(node_ids))
    for e in edg_new:
        graph.addEdge(e[0],e[1],e[2])
    print(graph.FindMinimumCycle())

def shortest_path(start,nodes,edges):#shortest path using bellman-ford algorithm
    "bellman ford for shortest path problem"
    dist={}
    parent={}
    b={}
    for id in nodes:
        b.update({id:False})
        parent.update({id:None})#-1 stands for unreachable
        dist.update({id:np.Infinity})#very high number, unreachable through any path
    b[start]=True
    parent[start]=None
    dist[start]=1
    q=[]
    q.append(start)
    while not len(q)==0:
        u=q.pop(0)
        b[u]=False
        for e in edges:
            if e[0]==u:#foreach v in u.adj()
                v=e[1]
                if dist[u]*e[2]<dist[v]:
                    if not b[v]:
                        q.append(v)
                        b[v]=True
                    parent[v]=u
                    dist[v]=dist[u]+e[2]
    return parent,dist

def get_cycle(Last, edge):
    "gets the cycle described by a Last dictionary given by a shortest path alg. and the edge closing the cycle"
    res=[edge[1]]
    id=edge[0]
    while id!=None:
        if not id in res:
            res.append(id)
            id=Last[id]
        else:
            break
    return res

def get_path(Last, end):
    "gets the path from a shortest path alg."
    res=[end]
    id=end
    while Last[id]!=None:
        if not Last[id] in res:
            res.append(Last[id])
            id=Last[id]
        else:
            break
    return res

def shortest_cycle(nodes,edges):
    "this function finds the shortest cycle in a graph with no negative cycles"
    #very interesting classsic solution that breaks in case of negative cycles
    #The problem is that the whole point of the arbitrage problem is to find negative cycles in a graph :(
    #so this is not a valid solution
    best =[]
    best_len = 100000000000
    for id in nodes:
        print(id)
        Last, dist =shortest_path(id,nodes,edges)
        for e in edges:
            if e[1]==id:#for each edge entering id
                cycle_val=dist[e[0]]*e[2]
                print(e," ",get_path(Last,e[0])," ",cycle_val)
                if cycle_val<best_len:
                    best_len=cycle_val
                    best=get_cycle(Last, e)
        print("\n")
    return best
                

def main():
    "main function for classical_arb_solver_v2.py"
    edg,vtc,ctv=atq.get_problem()
    #edg=atq.test_values()
    edg_small=atq.make_small(edg)
    #print("Edges are:\n",edg_small,"\n",len(edg_small))
    edg_subset=atq.make_subset(edg_small,35)
    #print("Edge subset is\n",edg_subset,"\n",len(edg_subset))
    edg_subset_log=atq.logarithm_on_all(edg_subset)
    #translate_in_mingraph(edg_small)
    '''nodes=get_node_ids(edg_small)
    #edg_small=atq.logarithm_on_all(edg_small)
    best=shortest_cycle(nodes,edg_small)
    print("Best sol found is:\n",best)
    
    qubo=atq.get_qubo(edg_subset,10,10)
    print("Qubo is:\n",qubo,"\n")'''
    solution=arbitrage_classic_solver(edg_subset_log)
    #qubo_solution=arbitrage_to_qubo_classic_solver(qubo)
    print(solution)
    #print(qubo_solution)
    sum=atq.arbitrage_cycle_multiplier_calc(edg_subset_log,solution)
    #qubo_sum=arbitrage_cycle_multiplier_calc(edg_small,qubo_solution)
    print(sum," -> ",2.0**sum)
    print(atq.natural_solution(edg_subset_log,solution,vtc,ctv))
    #print(qubo_sum," -> ",2.0**qubo_sum)

if __name__ == '__main__':
    main()