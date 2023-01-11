import random
import numpy as np

from Brain import *
from Constants import *


MUTATE_RATE = 0.8
MUTATION_N = 3


def mutate(x):
    if random.random() <= MUTATE_RATE:
        index = random.randint(0,N_CONECTIONS-1)
        x[1][index] = random.random()

    return x

def cross(father,x):
    son = np.zeros((2,N_CONECTIONS))

    for i in range(N_CONECTIONS):
        if random.random() < 0.5 and not(father[0,i] in x[0,0:]):
            son[0][i] = father[0][i]
            son[1][i] = father[1][i]
        else:
            son[0][i] = x[0][i]
            son[1][i] = x[1][i]

    return son

if __name__ == "__main__":
    a = random_genoma(BRAIN_STRUCTURE,N_CONECTIONS)
    b = random_genoma(BRAIN_STRUCTURE,N_CONECTIONS)

    print("PADRES")
    print(a)
    print(b)

    print("HIJOS")
    print(cross(a,b))