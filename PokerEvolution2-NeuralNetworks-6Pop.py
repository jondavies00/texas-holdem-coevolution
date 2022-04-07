#!/usr/bin/env python
# coding: utf-8

import random
import math
from datetime import datetime
from re import L
import numpy as np
import poker
import sys
import sys
import matplotlib.pyplot as plt
from pathos.multiprocessing import ProcessingPool as Pool
import multiprocessing
import time
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, r'C:\Users\jonat\OneDrive\Documents\Computer Science Degree\Year 3\Project\Implementation\poker')
import SixPlayerPoker as spp
import cProfile
import pstats



from deap import base
from deap import creator
from deap import tools


PREFLOP_INPUTS = 8
POSTFLOP_INPUTS = 7

numInputNodes1 = 8
numHiddenNodes1 = 5
numOutputNodes1 = 4

numInputNodes2 = 7
numHiddenNodes2 = 5
numOutputNodes2 = 4

PREFLOP_SIZE = (((numInputNodes1+1) * numHiddenNodes1) + (numHiddenNodes1 * numOutputNodes1))
#print(PREFLOP_SIZE)
POSTFLOP_SIZE = (((numInputNodes2+1) * numHiddenNodes2) + (numHiddenNodes2 * numOutputNodes2))

IND_SIZE = PREFLOP_SIZE + POSTFLOP_SIZE

def evaluateIndiv(indiv, pops):
    '''Run a poker game indiv'''
    g = spp.Game('evolve', small_blind=10, max_hands=100)
    opponentIndex = np.random.choice(players_per_pop, size=5, replace=False)
    #print(indiv, pop, opponentIndex)
    ind_pop = indiv.id
    opponents = [indiv]
    for i in range(len(pops)):
        if i+1 != ind_pop: #Ensure we do not pick from the same population as the individual
            last, opponentIndex = opponentIndex[-1], opponentIndex[:-1]
            opponents.append(pops[i][last]) # Random index
    # Take 6 individuals, assign their strategies to the players and run a game
    for (c,ind) in enumerate(opponents):
        if c == 0:
            g.assign_network_weights(indiv[:PREFLOP_SIZE], indiv[PREFLOP_SIZE:], c)
        else:
            g.assign_network_weights(ind[:PREFLOP_SIZE], ind[PREFLOP_SIZE:], c)
    profile = cProfile.Profile()
    profile.runcall(g.begin())
    ps = pstats.Stats(profile)
    ps.print_stats()
    pc = g.get_all_player_chips()
    chips = pc[0]
    sorted_chips = list(pc.values())
    sorted_chips.sort()
    if chips == 0:
        return 0
    if chips == sorted_chips[5]:
        return 6
    elif chips == sorted_chips[4]:
        return 5
    elif chips == sorted_chips[3]:
        return 4
    elif chips == sorted_chips[2]:
        return 3
    elif chips == sorted_chips[1]:
        return 2
    else:
        return 1

    net_chips = g.get_player_chip_count(0) -20000
    return net_chips

def evaluatePop(pop, belongs_to):
    return [evaluateIndiv(i, belongs_to) for i in pop]

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
toolbox.register("evaluate", evaluatePop)
toolbox.register("select", tools.selTournament, tournsize=5)

toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.2, indpb=0.05)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def initPopulation(inds, ind_init, size, ids):
    return inds(ind_init(id = ids) for i in range(size))

toolbox.register("population", initPopulation, list, toolbox.individual, size=1, ids=None)
#print(IND_SIZE)

total_players = 120 # Must be a multiple of 6
players_per_pop = total_players // 6

#Create 6 populations of 20 players with relevant ids
pop1 = toolbox.population(size=players_per_pop, ids=1)
pop2 = toolbox.population(size=players_per_pop, ids=2)
pop3 = toolbox.population(size=players_per_pop, ids=3)
pop4 = toolbox.population(size=players_per_pop, ids=4)
pop5 = toolbox.population(size=players_per_pop, ids=5)
pop6 = toolbox.population(size=players_per_pop, ids=6)
populations = [pop1,pop2,pop3,pop4,pop5,pop6]


logbook1 = tools.Logbook()
logbook2 = tools.Logbook()
logbook3 = tools.Logbook()
logbook4 = tools.Logbook()
logbook5 = tools.Logbook()
logbook6 = tools.Logbook()
logbooks = [logbook1, logbook2,logbook3,logbook4,logbook5,logbook6]
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)
invalid_inds = []
if __name__ == "__main__":

    pool = multiprocessing.Pool()
    toolbox.register("map", pool.starmap)

    def evaluate_multithread(pop, new_populations):
        return [toolbox.evaluate(ind,pop,new_populations) for ind in pop]

    # results = multiprocessing.Pool().starmap(evaluate_multithread, [(populations[0], populations),(populations[1], populations),
    #                                                                     (populations[2], populations),(populations[3], populations),
    #                                                                     (populations[4], populations),(populations[5], populations)])
    #fitnesses = [result for result in results]
    fitnesses = []
    # t1 = time.time()
    # for i,p in enumerate(populations):
    #     print('p%i'%i)
    #     fitnesses.append([toolbox.evaluate(ind, p,populations) for ind in p])
    # t2 = time.time()
    # print("Time for evaluation: ", t2-t1)
    # for n,p in enumerate(populations):        
    #     for (i,ind) in enumerate(p):
    #         ind.fitness.values = fitnesses[n][i],


    NGEN = 100
    for g in range(NGEN):
        
        print("-- Generation %i --" % g)
        
        new_populations = []
        for p in populations:
            offspring = toolbox.select(p, len(p))
            offspring = list(map(toolbox.clone, offspring))
            #print(offspring)
            new_populations.append(offspring)
        
        #print(new_populations)
        for new_pop in new_populations:
            for mutant in new_pop:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        
        invalid_inds = []
        for i,new_pop in enumerate(new_populations):
            invalid_inds.append([ind for ind in new_pop if not ind.fitness.valid])
        #opulations = invalid_inds
        t1 = time.time()
        fitnesses = toolbox.map(toolbox.evaluate, [(invalid_inds[0], invalid_inds),(invalid_inds[1], invalid_inds),(invalid_inds[2], invalid_inds),
                                                    (invalid_inds[3], invalid_inds),(invalid_inds[4], invalid_inds),(invalid_inds[5], invalid_inds)])
        print("Time for all 120 invidiuals to be evaluated = ", time.time() - t1)
        for p,inds in enumerate(invalid_inds):      
            
            for (i,ind) in enumerate(inds):
                ind.fitness.values = fitnesses[p][i],
        for i,new_pop in enumerate(invalid_inds):
            populations[i][:] = new_pop
            record = stats.compile(new_pop)
            logbooks[i].record(gen=g, **record)



    indiv1 = tools.selBest(pop1, 1)[0]
    indiv2 = tools.selBest(pop2, 2)[0]
    indiv3 = tools.selBest(pop3, 3)[0]
    indiv4 = tools.selBest(pop4, 4)[0]
    indiv5 = tools.selBest(pop5, 5)[0]
    indiv6 = tools.selBest(pop6, 6)[0]
    print(indiv1)
    print(indiv2)
    import pickle as pickle
    pickle.dump(indiv1, open( "p1.p", "wb" ) )
    pickle.dump(indiv2, open( "p2.p", "wb" ) )
    pickle.dump(indiv3, open( "p3.p", "wb" ) )
    pickle.dump(indiv4, open( "p4.p", "wb" ) )
    pickle.dump(indiv5, open( "p5.p", "wb" ) )
    pickle.dump(indiv6, open( "p6.p", "wb" ) )



    def testRandom(indiv):
        g = spp.Game(True, small_blind=10, max_hands=100)
        g.assign_network_weights(indiv[:PREFLOP_SIZE], indiv[PREFLOP_SIZE:], 0)
        g.begin
        net_chips = g.get_player_chip_count(0)
        return net_chips



    # print(testRandom(indiv1))
    # print(evaluate(indiv1, pop1))
    indiv1F = []
    for i in range(100):
        indiv1F.append(testRandom(indiv1))


    import matplotlib.pyplot as plt
    print(np.mean(indiv1F))
    plt.xlabel('Hand')
    plt.ylabel('Fitness')
    plt.plot(np.arange(100),indiv1F, label='Best Individual')

    plt.legend(loc='upper right')
    plt.show()



    avgs = logbooks[1].select("avg")
    print(avgs)



    pop = [indiv1]
    pop.append(toolbox.population(n=5))


    indiv1F, otherF = [], []
    for i in range(100):
        fitnesses = toolbox.evaluate(pop, True)
        indiv1F.append(fitnesses[0][0])
        if indiv1F[i] > 120000:
            print(indiv1F)
        otherF.append(sum(fitnesses[0][1:6])/5)


