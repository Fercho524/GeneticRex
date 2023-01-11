import numpy as np
import random

from Constants import *

BRAIN_STRUCTURE = [4,7,7,2]

def sigmoid(x):
    return 1 / (1 + np.e**(-x))


def relu(x):
    return max(0,x)


class NeuralNetwork:
    def __init__(self, weights):
        self.weights = weights

    def predict(self, x):
        result = x
        
        for l in range(len(self.weights)):
            result = np.matmul(result,self.weights[l])
        
        return result


class Brain:
    def __init__(self, genoma, structure):
        self.weights = []
        self.genoma = np.array(genoma)
        self.structure = structure

        neuron_id = 0

        # Construyes los pesos capa por capa
        for layer in range(1,len(self.structure)):
            # El tamaño de la matriz es el número de neuronas de la capa anterior por el número de neuronas de esta capa
            layer_weights = np.zeros((self.structure[layer-1],self.structure[layer]))
            ids = list(self.genoma[:][0])
            
            for x,y in np.ndindex(layer_weights.shape):
                # Recorremos todas las conexiones y si la conexión con un id está activa, cambiamos el peso
 
                if neuron_id in ids:
                    weigth_index = ids.index(neuron_id)               
                    layer_weights[x][y] = self.genoma[1,weigth_index]
                
                neuron_id+= 1
            
            self.weights.append(layer_weights)
        
        self.neural_network = NeuralNetwork(self.weights)

    def predict(self,enviroment):
        prediction = self.neural_network.predict(enviroment)
        action = 0

        if prediction[0]> prediction[1]:
            action = 2
        elif prediction[1]> prediction[0]:
            action = 1  

        return action   



def random_genoma(brain_shape,n_conections):
    total_conections = 0
    
    for i in range(len(brain_shape)-1):
        total_conections+= brain_shape[i]*brain_shape[i+1]

    conections_ids = list(np.arange(0,total_conections))
    conections = random.sample(conections_ids,n_conections)
    weights = list(np.random.randn(n_conections))

    return np.array([conections,weights])


# Brain of Dinosaurs
if __name__ == "__main__":
    genoma = random_genoma(BRAIN_STRUCTURE,N_CONECTIONS)
    print(genoma)

