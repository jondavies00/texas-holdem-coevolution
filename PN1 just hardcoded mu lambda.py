#!/usr/bin/env python
# coding: utf-8

from pickle import TRUE
import random
import math
from datetime import datetime
from re import L
from joblib import Parallel
import numpy as np
import poker
import sys
import sys
import matplotlib.pyplot as plt
from pathos.multiprocessing import ProcessingPool as Pool
import multiprocessing as mp
import time
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, r'C:\Users\jonat\OneDrive\Documents\Computer Science Degree\Year 3\Project\Implementation\poker')
import ParetoSixPlayerPoker as spp
import cProfile
import pstats
import copy
import pickle as pickle

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
    return (f/evals)-1000,

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax, id=None)

def initIndividual(weights, id):
    ind = weights(random.uniform(-1.0, 1.0) for _ in range(IND_SIZE))
    ind.id = id
    return ind

toolbox = base.Toolbox()

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

max_hands = 200 # Maximum amount of hands to play for evaluation
evals = 5
total_players = 120 # Must be a multiple of 6

PARETO_MATRIX = np.zeros((total_players, total_players))

pop = toolbox.population(size=total_players, ids=0)

logbook = tools.Logbook()
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

def eaMuPlusLambda(population, toolbox, mu, lambda_, cxpb, mutpb, ngen, stats=None,
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
    for gen in range(1, NGEN+1):
        print("GEN: %i" % gen)


        # Select the next generation individuals
        offspring = algorithms.varOr(population, toolbox,lambda_, cxpb, mutpb)

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

        population[:] = toolbox.select(population + offspring, mu)

    return population, logbook

CXPB = 0.5
MUTPB = 0.2
NGEN = 100
MU = 120
LAMBDA = 240

if __name__ == "__main__":
    pool = mp.Pool()
    toolbox.register("map", pool.map)
    
    pop, log = eaMuPlusLambda(pop, toolbox,MU, LAMBDA, CXPB, MUTPB, NGEN, stats)

    indiv1 = tools.selBest(pop, 1)[0]

    pickle.dump(indiv1, open( "saves/Adapted Hardcoded Strategy/p1.p", "wb" ) )
    pickle.dump(log, open("saves/Adapted Hardcoded Strategy/avg_fitness.p", "wb"))

