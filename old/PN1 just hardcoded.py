#!/usr/bin/env python
# coding: utf-8

import random
import numpy as np

import sys
import sys
import matplotlib.pyplot as plt
import multiprocessing as mp

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, r'C:\Users\jonat\OneDrive\Documents\Computer Science Degree\Year 3\Project\Implementation\poker')
import ParetoSixPlayerPoker as spp

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

PREFLOP_INPUTS = 8
POSTFLOP_INPUTS = 7

numInputNodes1 = 8
numHiddenNodes1 = 5
numOutputNodes1 = 3

numInputNodes2 = 7
numHiddenNodes2 = 5
numOutputNodes2 = 3

PREFLOP_SIZE = (((numInputNodes1+1) * numHiddenNodes1) + (numHiddenNodes1 * numOutputNodes1))
#print(PREFLOP_SIZE)
POSTFLOP_SIZE = (((numInputNodes2+1) * numHiddenNodes2) + (numHiddenNodes2 * numOutputNodes2))

IND_SIZE = PREFLOP_SIZE + POSTFLOP_SIZE

#Just an attempt to see if only using hardcoded evaluation produces good strategy

def evaluatePlayer(indiv):
    '''Play the player against the hardcoded strategy'''
    f=0
    for i in range(evals):
        game = spp.Game('evaluate-hardcoded', small_blind=2, max_hands=max_hands)
        game.assign_network_weights(indiv[:PREFLOP_SIZE], indiv[PREFLOP_SIZE:], 0)
        
        game.begin()
        fits = game.get_player_chip_count(0)
        f += fits
    #print(f/evals)
    return (f/evals)-1000,

def evaluateHOFs(six_indivs, max_hands):
    game = spp.Game('evolve', small_blind=2, max_hands=max_hands)
    ''' Take 6 individuals and play a game with them, returning the last player's (one we care about) fitness'''
    for i in range(6):
        to_play = six_indivs[i]
        game.assign_network_weights(to_play[:PREFLOP_SIZE], to_play[PREFLOP_SIZE:], i)
    game.begin()
    # pc = game.get_all_player_chips()
    # chips = pc[i]
    fits = game.get_player_chip_count(0)
    f = fits
    return f,


def evaluateRandoms(six_indivs,max_hands ):
    game = spp.Game('evolve', small_blind=2, max_hands=max_hands)
    ''' Take 6 individuals and play a game with them, returning the last player's (one we care about) fitness'''
    for i in range(6):
        to_play = six_indivs[i]
        game.assign_network_weights(to_play[:PREFLOP_SIZE], to_play[PREFLOP_SIZE:], i)
    game.begin()
    fits = game.get_player_chip_count(0)
    f = fits
    return f,

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
toolbox.register("evaluate", evaluatePlayer)



toolbox.register("select", tools.selTournament, tournsize=5)

toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.2, indpb=0.05)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxOnePoint)

def initPopulation(inds, ind_init, size, ids):
    return inds(ind_init(id = i) for i in range(size))

toolbox.register("population", initPopulation, list, toolbox.individual, size=1, ids=None)
#print(IND_SIZE)

max_hands = 200 # Maximum amount of hands to play for evaluation
evals = 1
total_players = 102 # Must be a multiple of 6

PARETO_MATRIX = np.zeros((total_players, total_players))


pop = toolbox.population(size=total_players, ids=0)


logbook = tools.Logbook()
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)


def eaSimple(population, toolbox, cxpb, mutpb, ngen, stats=None,
             halloffame=None, verbose=__debug__):
             
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness

    invalid_ind=[ind for ind in population if not ind.fitness.valid]

    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)

    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)

    if verbose:
        print(logbook.stream)
    # Begin the generational process
    for gen in range(1, ngen + 1):
        print("GEN: %i" % gen)


        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))

        # Vary the pool of individuals
        offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind=[ind for ind in offspring if not ind.fitness.valid]
    
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)

        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        #Play hardcoded strategies with best individual from each population
        # rf = 0
        # for e in range(evals):
        #     rf += evaluatePlayer(tools.selBest(offspring, 1)[0])[0]
        # print((rf/evals) - 1000)

        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

        population[:] = offspring

    return population, logbook

CXPB = 0.5
MUTPB = 0.2
NGEN = 100
hof = tools.HallOfFame(6)

if __name__ == "__main__":
    #pool = multiprocessing.Pool(processes=5)
    #toolbox.register("map", pool.map)
    
    pool = mp.Pool()
    toolbox.register("map", pool.map)
    

    pop, log = eaSimple(pop, toolbox, CXPB, MUTPB, NGEN, stats, hof)

    print(log)


    indiv1 = tools.selBest(pop[0], 1)[0]
    indiv2 = tools.selBest(pop[1], 2)[0]
    indiv3 = tools.selBest(pop[2], 3)[0]
    indiv4 = tools.selBest(pop[3], 4)[0]
    indiv5 = tools.selBest(pop[4], 5)[0]
    indiv6 = tools.selBest(pop[5], 6)[0]

    import pickle as pickle
    pickle.dump(indiv1, open( "p1.p", "wb" ) )
    pickle.dump(indiv2, open( "p2.p", "wb" ) )
    pickle.dump(indiv3, open( "p3.p", "wb" ) )
    pickle.dump(indiv4, open( "p4.p", "wb" ) )
    pickle.dump(indiv5, open( "p5.p", "wb" ) )
    pickle.dump(indiv6, open( "p6.p", "wb" ) )

    pickle.dump(log, open("obj_f", "wb"))

    p1_f = log[0]
    p2_f = log[1]
    p3_f = log[2]
    p4_f = log[3]
    p5_f = log[4]
    p6_f = log[5]
    import matplotlib.pyplot as plt

    plt.xlabel('Gen')
    plt.ylabel('Fitness')
    plt.plot(np.arange(NGEN),p1_f, label='FitnessP1 vs random strategy')
    plt.plot(np.arange(NGEN),p2_f, label='FitnessP2 vs random strategy')
    plt.plot(np.arange(NGEN),p3_f, label='FitnessP3 vs random strategy')
    plt.plot(np.arange(NGEN),p4_f, label='FitnessP4 vs random strategy')
    plt.plot(np.arange(NGEN),p5_f, label='FitnessP5 vs random strategy')
    plt.plot(np.arange(NGEN),p6_f, label='FitnessP6 vs random strategy')
    plt.legend(loc='upper right')
    plt.show()


