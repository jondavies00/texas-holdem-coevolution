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
import copy


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

def evaluatePopulation(individuals):
    '''Takes a whole population of individuals'''
    #print("evaluating")
    indivs = copy.deepcopy(individuals)
    indivs_refer = []
    for i in range(len(indivs)):
        indivs_refer.append(list(range(len(indivs[i]))))
    
    f1, f2, f3, f4, f5, f6 = [0]*len(indivs[0]),[0]*len(indivs[1]),[0]*len(indivs[2]),[0]*len(indivs[3]),[0]*len(indivs[4]),[0]*len(indivs[5])
    fitnesses = [f1,f2,f3,f4,f5,f6] 
    finished = False
    #create as many groups of 6 as poss
    while not finished:
        #print("notfinished")
        oppIndexes = []
        game = spp.Game('evolve', small_blind=10, max_hands=1000)
        for i in range(6):
            if len(indivs_refer[i]) == 0:
                # pick from whole population instead
                oppIndex=random.randint(0, 19)
                to_play = populations[i][oppIndex]
            else:
                oppIndex=indivs_refer[i][random.randint(0, len(indivs_refer[i])-1)] # Take a random opponent from each population that do not yet have a fitness
                to_play = indivs[i][oppIndex]
                indivs_refer[i].remove(oppIndex)
                oppIndexes.append((oppIndex, to_play.id-1))
            game.assign_network_weights(to_play[:PREFLOP_SIZE], to_play[PREFLOP_SIZE:], i)
        game.begin()
        pc = game.get_player_fitnesses()
        for i in oppIndexes:
            #player_pop = i[0]
            # chips = pc[i[1]]
            # fitnesses[i[1]][i[0]] = (chips-20000,)
            fitnesses[i[1]][i[0]] = (pc[i[1]],)
        finished = all([len(p)==0 for p in indivs_refer]) #if all indivs are empty
    return fitnesses
    
def evaluateHOFs(six_indivs):
    game = spp.Game('evolve', small_blind=10, max_hands=1000)
    ''' Take 6 individuals and play a game with them, returning the last player's (one we care about) fitness'''
    for i in range(6):
        to_play = six_indivs[i]
        game.assign_network_weights(to_play[:PREFLOP_SIZE], to_play[PREFLOP_SIZE:], i)
    game.begin()
    # pc = game.get_all_player_chips()
    # chips = pc[i]
    fits = game.get_player_fitnesses()
    f = fits[i]
    return f,
    sorted_chips = list(pc.values())
    sorted_chips.sort()
    if chips == 0:
        fitness = (0,)
    elif chips == sorted_chips[5]:
        fitness = (6,)
    elif chips == sorted_chips[4]:
        fitness = (5,)
    elif chips == sorted_chips[3]:
        fitness = (4,)
    elif chips == sorted_chips[2]:
        fitness = (3,)
    elif chips == sorted_chips[1]:
        fitness = (2,)
    else:
        fitness = (1,)
    return fitness

def evaluateRandoms(six_indivs):
    game = spp.Game('evolve', small_blind=10, max_hands=1000)
    ''' Take 6 individuals and play a game with them, returning the last player's (one we care about) fitness'''
    for i in range(6):
        to_play = six_indivs[i]
        game.assign_network_weights(to_play[:PREFLOP_SIZE], to_play[PREFLOP_SIZE:], i)
    game.begin()
    # fits = game.get_player_fitnesses()
    # f = fits[i]
    f = game.get_player_chip_count(5)
    return f,

def evaluateHardcoded(indiv):
    game = spp.Game('testvstag', small_blind=10, max_hands=1000)
    ''' Take 6 individuals and play a game with them, returning the last player's (one we care about) fitness'''

    game.assign_network_weights(indiv[:PREFLOP_SIZE], indiv[PREFLOP_SIZE:], 5)
    game.begin()
    # fits = game.get_player_fitnesses()
    # f = fits[i]
    f = game.get_player_chip_count(5)
    return f,

def addFitnessLists(f1, f2):
    '''Adds two 2D lists of fitnesses, and return the 2D list of fitnesses'''
    summed = [[],[],[],[],[],[]]
    for i in range(len(f1)):
        p1 = f1[i]
        p2 = f2[i]
        untupped1 = [x[0] for x in p1]
        untupped2 =[x[0] for x in p2]
        summed[i] =  [(sum(x),) for x in list(zip(untupped1,untupped2))]
    return summed

def divFitnessList(f1, d):
    '''Takes a 2D fitness list and divides each value by d, and returns a 2D list'''
    divved = [[],[],[],[],[],[]]
    for i in range(len(f1)):
        p1 = f1[i]
        untupped1 = [x[0] for x in p1]
        divved[i] =  [(x/d,) for x in untupped1]
    return divved

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
toolbox.register("evaluate", evaluatePopulation)



toolbox.register("select", tools.selTournament, tournsize=5)

toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.2, indpb=0.05)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxOnePoint)

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

def eaSimple(population, toolbox, cxpb, mutpb, ngen, pool, stats=None,
             halloffame=None, verbose=__debug__):
             
    obj_log = tools.Logbook()
    obj_log.header = ['gen', 'nevals'] + (stats.fields if stats else [])
    objective_fitness = [[],[],[],[],[],[]]
    logbooks = [tools.Logbook(),tools.Logbook(),tools.Logbook(),tools.Logbook(),tools.Logbook(),tools.Logbook()]
    for logbook in logbooks:
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = []
    for p in population:
        invalid_ind.append([ind for ind in p if not ind.fitness.valid])


    # fitnesses = toolbox.evaluate(invalid_ind)
    # for i in range(4):
    #     addFitnessLists(fitnesses, toolbox.evaluate(invalid_ind))
    async_results = []
    with multiprocessing.Pool(processes=5) as poo:
        for i in range(5):
            async_results.append(poo.apply_async(toolbox.evaluate, (invalid_ind,)))
        poo.close()
        poo.join()

    results =  [[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20]
    
    for i, async_result in enumerate(async_results):
        results = addFitnessLists(results,async_result.get())

    fitnesses = divFitnessList(results, 5) # generates an average fitness over 5 games
    for i in range(len(invalid_ind)):
        for ind, fit in zip(invalid_ind[i], fitnesses[i]):
            ind.fitness.values = fit

    if halloffame is not None:
        for p in population:
            halloffame.insert(tools.selBest(p, 1)[0])
    # for i,p in enumerate(populations):
    #     record = stats.compile(p) if stats else {}
    #     logbooks[i].record(gen=0, nevals=len(invalid_ind), **record)
    # if verbose:
    #     [print(logbook.stream) for logbook in logbooks]

    # Begin the generational process
    for gen in range(1, ngen + 1):
        print("GEN: %i" % gen)


        # Select the next generation individuals
        offspring = [toolbox.select(p, len(p)) for p in population]

        # Vary the pool of individuals
        offspring = [algorithms.varAnd(o, toolbox, cxpb, mutpb) for o in offspring]

        # Evaluate the individuals with an invalid fitness
        invalid_ind = []
        for p in offspring:
            invalid_ind.append([ind for ind in p if not ind.fitness.valid])
        
        async_results = []
        with multiprocessing.Pool(processes=5) as poo:
            for i in range(5):
                async_results.append(poo.apply_async(toolbox.evaluate, (invalid_ind,)))
            poo.close()
            poo.join()
        results =  [[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20]
        for i, async_result in enumerate(async_results):
            results = addFitnessLists(results,async_result.get())

        fitnesses = divFitnessList(results, 5) # generates an average fitness over 5 games

        for i in range(len(invalid_ind)):
            for ind, fit in zip(invalid_ind[i], fitnesses[i]):
                ind.fitness.values = fit
        # Play the hall of fame individuals with the best individual from each population (to measure perforamnce)
        # for i in range(6):
        #     of = evaluateHOFs([hof[i], hof[i], hof[i], hof[i], hof[i], tools.selBest(offspring[i], 1)[0]])
        #     objective_fitness[i].append(of[0])

        #Play random individuals against the best from each population to measure performance.
        # for i in range(6):
        #     rf = 0
        #     for e in range(5):
        #         rf += evaluateRandoms([toolbox.individual(), toolbox.individual(),toolbox.individual(),toolbox.individual(),toolbox.individual(),tools.selBest(offspring[i], 1)[0]])[0]
        #     objective_fitness[i].append(rf/5)
        # print(np.mean(objective_fitness))

        for i in range(6):
            rf = 0
            for e in range(5):
                rf += evaluateHardcoded(tools.selBest(offspring[i], 1)[0])[0]
            objective_fitness[i].append(rf/5)
        print(np.mean(objective_fitness))
        # Update the hall of fame with the generated individuals
        # if halloffame is not None:
        #     for p in offspring:
        #         halloffame.insert(tools.selBest(p, 1)[0])

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        # record = stats.compile(population) if stats else {}
        #logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        #if verbose:
            #print (logbook.stream)

    return population, objective_fitness

CXPB = 0.5
MUTPB = 0.2
NGEN = 1000
hof = tools.HallOfFame(6)

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=5)
    toolbox.register("map", pool.map)

    

    pop, log = eaSimple(populations, toolbox, CXPB, MUTPB, NGEN,pool, stats, hof)

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


