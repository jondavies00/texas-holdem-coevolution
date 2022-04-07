### Allows the user to play against an evolved poker agent
import pickle 
import SixPlayerPoker as spp

from deap import base
from deap import creator
from deap import tools

import random

PREFLOP_INPUTS = 8
POSTFLOP_INPUTS = 7

numInputNodes1 = 8
numHiddenNodes1 = 5
numOutputNodes1 = 3

numInputNodes2 = 7
numHiddenNodes2 = 5
numOutputNodes2 = 3

PREFLOP_SIZE = (((numInputNodes1+1) * numHiddenNodes1) + (numHiddenNodes1 * numOutputNodes1))
POSTFLOP_SIZE = (((numInputNodes2+1) * numHiddenNodes2) + (numHiddenNodes2 * numOutputNodes2))

IND_SIZE = PREFLOP_SIZE + POSTFLOP_SIZE

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax, id=None)

def initIndividual(weights, id):
    ind = weights(random.uniform(-1.0, 1.0) for _ in range(IND_SIZE))
    ind.id = id
    return ind

toolbox = base.Toolbox()
#toolbox.register("attr_float", random.uniform, -1.0, 1.0)

toolbox.register("individual", initIndividual, creator.Individual,
                id=None)

class EvolvedPlay:
    
    def __init__(self):
        self.players = []

    def loadPlayer(self, save_files):
        if len(save_files) != 5:
            raise ValueError('Invalid amount of saves')
        for fn in save_files:
            self.players.append(pickle.load(open(fn, "rb" )))

    def playAI(self):
        g = spp.Game('manual', 20, 100, 20000)
        pfw = (numInputNodes1+1) * numHiddenNodes1 + (numHiddenNodes1 * numOutputNodes1)
        for i,p in enumerate(self.players):
            g.assign_network_weights(p[:pfw], p[pfw:], i+1)
        g.begin()

e = EvolvedPlay()
e.loadPlayer(['p2.p','p3.p','p4.p','p5.p','p6.p',])
e.playAI()