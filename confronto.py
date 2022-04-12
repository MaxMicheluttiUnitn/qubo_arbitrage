import classical_arb_solver_v3 as classic
import dwave_arb_solver as quantum
import numpy as np
import arbtoqubo_v2 as atq

MAXSIZE=35
PRIMO_CONSTRAINT=20
SECONDO_CONSTRAINT=20

def print_on_file_best_solutions(edges,table,valtocod,codtoval):
    i=0
    for row in table:
        if i>30:
            break
        with open('tmp_output'+str(i)+'.txt', 'w') as f:
            sol=[]
            for j in range(len(row)):
                sol.append(row[j])
                if row[j]:
                    f.write(str(edges[j]))
                    f.write(",\n")
            f.write("\n")
            f.write(str(sol))
    

def main():
    print("Getting problem...")
    edges,valtocod,codtoval=atq.get_problem()
    edg_small=atq.make_small(edges)
    edg_subset=atq.make_subset(edg_small,MAXSIZE)
    print("Solving classic...")
    edg_log=atq.logarithm_on_all(edg_subset)
    classic_solution=classic.arbitrage_classic_solver(edg_log)
    print(classic_solution)
    classic_adv=atq.arbitrage_cycle_multiplier_calc(edg_log,classic_solution)
    print(classic_adv," -> ", 2.0**classic_adv)
    print(atq.natural_solution(edg_log,classic_solution,valtocod,codtoval))
    print("Building QUBO Problem...")
    qubo=atq.get_qubo(edg_subset,PRIMO_CONSTRAINT,SECONDO_CONSTRAINT)
    print("Getting results...")
    res=quantum.solve(qubo)
    print("Parsing results...")
    table=quantum.convert_response_to_numpy(res)
    print("Checking results...")
    print_on_file_best_solutions(edg_subset,table,valtocod,codtoval)
    '''sol,nrg,ocs=quantum.find_best_valid_solution(edg_subset,table,valtocod,codtoval)
    if(sol!=None):
        print(sol)
        print(nrg)
        print(ocs)
        print(atq.natural_solution(edg_subset,sol,valtocod,codtoval))
    else:
        print("No valid solution was found")'''


if __name__ =='__main__':
    main()