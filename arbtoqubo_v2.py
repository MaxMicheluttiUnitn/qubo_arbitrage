import numpy as np
import csv
import requests as req
import math
from os.path import exists

'''
url = "https://it.investing.com/currencies/streaming-forex-rates-majors"
resp = req.get(url)
print(resp.text)
'''

def read_csv(input_file_name):
    "this function reads the csv file from investing.com and initializes the variables of the problem"
    valuta_to_codice=dict()
    edges=[]
    codice_to_valuta=[]
    with open(input_file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:#popolo dizionario delle valute
            x=row['ï»¿"Simbolo"'].split('/')
            num=x[0]
            denom=x[1]
            if not (num in valuta_to_codice.keys()):#aggiungo num al dizionario delle valute
                valuta_to_codice.update({num: len(valuta_to_codice)})
                codice_to_valuta.append(num)
            if not (denom in valuta_to_codice.keys()):#aggiungo denom al dizionario delle valute
                valuta_to_codice.update({denom: len(valuta_to_codice)})
                codice_to_valuta.append(denom)
        #edge_matrix = np.zeros(shape=(len(valuta_to_codice),len(valuta_to_codice)), dtype=float)
    with open(input_file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:#popolo tabella del valore di scambio
            x=row['ï»¿"Simbolo"'].split('/')#row['ï»¿"Simbolo"'] has the format "VA1/VA2" and means that if i give 1 VA1 i receive row["Denaro"] VA2  
            num=x[0]#gets the numerator of the exchange
            denom=x[1]#gets the denominator of the exchange
            value=float((row['Denaro'].replace('.','')).replace(',','.'))# have to fix the string so that it can be parsed into a real number
            edges.append([valuta_to_codice[num],valuta_to_codice[denom],value])
            edges.append([valuta_to_codice[denom],valuta_to_codice[num],1.0/value])
            #edge_matrix[valuta_to_codice[num]][valuta_to_codice[denom]]=value
            #edge_matrix[valuta_to_codice[denom]][valuta_to_codice[num]]=1.0/value
    return valuta_to_codice, codice_to_valuta, edges

'''
def parse_input(file_name):
    if exists(file_name):
        valuta_to_codice,edges=read_csv(file_name)
    else:
        print("Errore: File non trovato")
        quit()
    return valuta_to_codice, edges

with open('tmp_output'+str(v)+'.txt', 'w') as f:
    for i in range(len(edges)):
        for j in range(len(edges)):
            f.write(str(tmp[i][j]))
            f.write(', ')
        f.write('\n')
'''

def logarithm_on_all(edges):
    "this function takes in input a square matrix and applies the logarithm in base 2 to every cell of the matrix"
    for i in range(len(edges)):
        edges[i][2]=math.log2(edges[i][2])
    return edges

def invert_sign_matrix(matrix):
    "this function takes in input a square matrix and changes the sign to every cell of the matrix"
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            matrix[i][j]=-matrix[i][j]
    return matrix

def make_arbitrage_qubo(edges,M1=10,M2=10):
    "this funcion takes in input the adj matrix of the graph and the list of its edges and computes the qubo matrix"
    edges = logarithm_on_all(edges)
    qubo= np.zeros(shape=(len(edges),len(edges)), dtype=float)
    #definizione di score del percorso
    for i in range(len(edges)):
        qubo[i][i]=edges[i][2]
    #nodes=0
    node_ids=[]
    for e in edges:
        if not (e[0] in node_ids):
            node_ids.append(e[0])
            #nodes+=1
        if not (e[1] in node_ids):
            node_ids.append(e[1])
            #nodes+=1
    #primo constraint (controllato, funziona a meraviglia)
    #convenzione: non esistono edge del tipo [x,x]
    for v in node_ids:#for i in v
        tmp=np.zeros(shape=(len(edges),len(edges)), dtype=int)
        for j in range(len(edges)):
            if v==edges[j][0]:
                tmp[j][j]=1
            if v==edges[j][1]:
                tmp[j][j]=-1
        for i in range(len(edges)):
            for j in range(len(edges)):
                if i!=j:
                    tmp[i][j]=2*tmp[i][i]*tmp[j][j]
        for i in range(len(edges)):
            tmp[i][i]*=tmp[i][i]
        #print(tmp)
        for i in range(len(edges)):
            for j in range(len(edges)):
                qubo[i][j]+=tmp[i][j]*(-M1)
    #secondo constraint
    for v in node_ids:#for i in v
        tmp=np.zeros(shape=(len(edges),len(edges)), dtype=int)
        for i in range(len(edges)):
            if v==edges[i][0]:
                for j in range(len(edges)):
                    if v==edges[j][0] and i!=j:
                        tmp[i][j]+=1
                        tmp[j][i]+=1
                        tmp[i][i]-=1
        for i in range(len(edges)):
            for j in range(len(edges)):
                qubo[i][j]+=tmp[i][j]*(-M2)
    qubo=invert_sign_matrix(qubo)
    return qubo

def test_values():
    "this function initializes the edge list with test values"
    edges =[[0,1,2.0],[1,0,0.5],[0,2,4.0],[2,0,0.25],[1,2,3.0],[2,1,1.0/3.0],[3,0,0.1],[0,3,10.0],[1,3,2.0],[3,1,0.5]]
    return edges

def get_qubo(edges=[],M1=10,M2=10):
    "this function reads the input and computes the qubo matrix for the arbitrage problem"
    # codtoval: lista che associa a ogni id una stringa col nome della valuta
    # valtocod: dizionario che associa a ogni stringa il relativo id
    # matrix: matrice di adiacenza del grafo con i pesi degli archi+
    # edges: lista di tutti i vertici del grafo
    #edges=test_values()
    if edges==[]:
        valtocod, codtoval, edges= read_csv('cambio_valute.csv')
    #matrix,edges = test_values()
    qubo = make_arbitrage_qubo(edges,M1,M2)
    return qubo

def get_problem():
    valtocod, codtoval, edges= read_csv('cambio_valute.csv')
    return edges

def matrix_mult(X,Y):
    if len(X[0])==len(Y):
        res=np.zeros(shape=(len(X),len(Y[0])),dtype=float)
        # iterate through rows of X
        for i in range(len(X)):
        # iterate through columns of Y
            for j in range(len(Y[0])):
                # iterate through rows of Y
                for k in range(len(Y)):
                    res[i][j] += X[i][k] * Y[k][j]
        return res

def make_small(edges):
    "this function reduces the size of the problem by eliminating all leaf nodes"
    #nodes=0
    node_ids={}
    for e in edges:
        if not (e[0] in node_ids):
            node_ids.update({e[0]:1})
            #nodes+=1
        else:
            node_ids[e[0]]+=1
        if not (e[1] in node_ids):
            node_ids.update({e[1]:1})
            #nodes+=1
        else:
            node_ids[e[1]]+=1
    keep=[]
    for i in node_ids.keys():
        if node_ids[i]>2:#if there exists less then 2 connections with the rest of the graph, the node is a leaf and can be ignored
            keep.append(i)
    #print(edge_matrix)
    new_edges=[]
    for e in edges:
        if e[0] in keep and e[1] in keep:
            new_edges.append([e[0],e[1],e[2]])
    #print(new_edges)
    return new_edges



def compute_solution_value(x,qubo):
    "this function takes an array of booleans and a qubo matrix and computes its score"
    matx=[x[:]]
    matx_tran=[]
    for v in x:
        matx_tran.append([v])
    tmp=matrix_mult(matx,qubo)
    tmp=matrix_mult(tmp,matx_tran)
    '''tmp=[0.0 for i in range(len(x))]
    for j in range(len(x)):
        for k in range(len(x)):
            tmp[j]+=(qubo[k][j]*x[k])
    sol=0
    for i in range(len(x)):
        sol+=(x[i]*tmp[i])
    #print(x,":",sol)'''
    return tmp[0][0]


def main():
    "main function for this program"
    #qubo=get_qubo()
    #print(qubo)
    X = [[12,7,3],
    [4 ,5,6],
    [7 ,8,9]]
    # 3x4 matrix
    Y = [[5,8,1,2],
        [6,7,3,0],
        [4,5,9,1]]
    print(matrix_mult(X,Y))
    #print(compute_solution_value([1,0,0,1],qubo))

if __name__=='__main__':
    main()
