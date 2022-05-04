#!/usr/bin/env python
# coding: utf-8

### Performs six-population single-objective coevolution

import random
import numpy as np
import sys
import sys

import multiprocessing
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, r'C:\Users\jonat\OneDrive\Documents\Computer Science Degree\Year 3\Project\Implementation\poker')
import ParetoSixPlayerPoker as spp
import pickle
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
        game = spp.Game('evolve', small_blind=10, max_hands=200)
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

total_players = 300 # Must be a multiple of 6

players_per_pop = 300 // 6



#Create 6 populations of 20 players with relevant ids
pop1 = toolbox.population(size=players_per_pop, ids=1)
pop2 = toolbox.population(size=players_per_pop, ids=2)
pop3 = toolbox.population(size=players_per_pop, ids=3)
pop4 = toolbox.population(size=players_per_pop, ids=4)
pop5 = toolbox.population(size=players_per_pop, ids=5)
pop6 = toolbox.population(size=players_per_pop, ids=6)
populations = [pop1,pop2,pop3,pop4,pop5,pop6]
evolvedIndiv = pickle.load(open("Gathering Results/saves/Adapted Hardcoded Strategy/p1.p", 'rb'))
for p in range(6):
    for i in range(2):
        to_append = copy.deepcopy(evolvedIndiv)
        to_append.id = p + 1
        # evolvedIndiv.id = p
        populations[p].append(to_append)

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
    res = []
    #results = []
    results =  [[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20]
    for i in range(evals):
        results = addFitnessLists(results, toolbox.evaluate(population))

    fitnesses = divFitnessList(results, evals) # generates an average fitness over 5 games
    for i in range(len(invalid_ind)):
        for ind, fit in zip(invalid_ind[i], fitnesses[i]):
            ind.fitness.values = fit

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
        #results = []
        # results =  [[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20]
        # for i in range(evals):
        #     with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        #         async_results.append(pool.apply_async(toolbox.evaluate, (invalid_ind,)))
        #     pool.close()
        #     pool.join()
        # for i, async_result in enumerate(async_results[0].get()):
        #     results = addFitnessLists(results,async_result)
        results =  [[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20,[(0,)]*20]
        for i in range(evals):
            results = addFitnessLists(results, toolbox.evaluate(population))

        fitnesses = divFitnessList(results, evals) # generates an average fitness 


        for i in range(len(invalid_ind)):
            for ind, fit in zip(invalid_ind[i], fitnesses[i]):
                ind.fitness.values = fit

        population[:] = offspring

        for i,p in enumerate(population):
            pickle.dump(p, open("Gathering Results/saves/Six-Population Reg Coevolution/population%i_gen%i.p" % (i, gen), 'wb'))


    return population

CXPB = 0.5
MUTPB = 0.2
NGEN = 100
evals = 10
hof = tools.HallOfFame(6)

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=5)
    toolbox.register("map", pool.map)

    

    pop = eaSimple(populations, toolbox, CXPB, MUTPB, NGEN,pool, stats, hof)