#!/usr/bin/env python
# coding: utf-8

### Performs single-objective coevolution

import random
import numpy as np

import sys
import sys

import multiprocessing
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, r'C:\Users\jonat\OneDrive\Documents\Computer Science Degree\Year 3\Project\Implementation\poker')
import ParetoSixPlayerPoker as spp

import copy
import pickle

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

max_hands = 200

def playPopulation(individuals, max_hands=max_hands):
    '''
    Takes one whole populations of individuals, plays a game of six random players and returns a list 
    of tuples (indivs and matrix)
    '''
    indivs = copy.deepcopy(individuals)
    indivs_and_matrix = []
    indivs_refer = list(range(len(indivs)))
    finished = False
    #create as many groups of 6 as poss
    while not finished:
        #print("notfinished")
        playing = []
        oppIndexes = []
        game = spp.Game('evolve', small_blind=2, max_hands=max_hands)
        for i in range(6):
            if len(indivs_refer) == 0:
                # pick from whole population instead
                oppIndex=random.randint(0, total_players-1)
                to_play = pop[oppIndex]
            else:
                oppIndex=indivs_refer[random.randint(0, len(indivs_refer)-1)] # Take a random opponent from each population that do not yet have a fitness
                to_play = indivs[oppIndex]
                indivs_refer.remove(oppIndex)
                oppIndexes.append((oppIndex, to_play.id-1))
            game.assign_network_weights(to_play[:PREFLOP_SIZE], to_play[PREFLOP_SIZE:], i)
            playing.append(to_play)
        game.begin()
        matrix = game.win_loss_matrix
        indivs_and_matrix.append((playing, matrix))
        finished = len(indivs_refer) == 0
    return indivs_and_matrix

def evaluatePopulation(individuals):
    '''Takes a whole population of individuals'''
    #print("evaluating")
    indivs = copy.deepcopy(individuals)
    indivs_refer = list(range(len(indivs)))


    fitnesses = [0]*total_players 
    finished = False
    #create as many groups of 6 as poss
    while not finished:
        #print("notfinished")
        oppIndexes = []
        game = spp.Game('evolve', small_blind=10, max_hands=200)
        for i in range(6):
            if len(indivs_refer) == 0:
                # pick from whole population instead
                oppIndex=random.randint(0, total_players-1)
                to_play = pop[oppIndex]
            else:
                oppIndex=indivs_refer[random.randint(0, len(indivs_refer)-1)] # Take a random opponent from each population that do not yet have a fitness
                to_play = indivs[oppIndex]
                indivs_refer.remove(oppIndex)
                oppIndexes.append(oppIndex)
            game.assign_network_weights(to_play[:PREFLOP_SIZE], to_play[PREFLOP_SIZE:], i)
        game.begin()
        pc = game.get_player_fitnesses()
        for c,i in enumerate(oppIndexes):
            fitnesses[i] = (pc[c],)
        finished = len(indivs_refer)==0 #if all indivs are empty
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
    for i in range(len(f1)):
        untupped1 = [x[0] for x in f1]
        untupped2 =[x[0] for x in f2]
        summed =  [(sum(x),) for x in list(zip(untupped1,untupped2))]
    return summed

def divFitnessList(f1, d):
    '''Takes a 2D fitness list and divides each value by d, and returns a 2D list'''
    for i in range(len(f1)):
        untupped1 = [x[0] for x in f1]
        divved =  [(x/d,) for x in untupped1]
    return divved

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax, id=None)

def initIndividual(weights, id):
    ind = weights(random.uniform(-1.0, 1.0) for _ in range(IND_SIZE))
    ind.id = id
    return ind

toolbox = base.Toolbox()

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


original = 100 # Must be a multiple of 6
seeded = 10
total_players = original + seeded

#Create 6 populations of 20 players with relevant ids
pop = toolbox.population(size=original, ids=1)

evolvedIndiv = pickle.load(open("Gathering Results/saves/Adapted Hardcoded Strategy/p1.p", 'rb'))

for i in range(seeded):
    to_append = copy.deepcopy(evolvedIndiv)
    # evolvedIndiv.id = p
    pop.append(to_append)

logbook = tools.Logbook()
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
    invalid_ind = [ind for ind in population if not ind.fitness.valid]

    results =  [(0,)]*total_players
    for i in range(evals):
        results = addFitnessLists(results, toolbox.evaluate(population))

    fitnesses = divFitnessList(results, evals) # generates an average fitness over 5 games

    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # Begin the generational process
    for gen in range(1, ngen + 1):
        print("GEN: %i" % gen)


        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))

        # Vary the pool of individuals
        offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]

        results =  [(0,)]*total_players
        for i in range(evals):
            results = addFitnessLists(results, toolbox.evaluate(population))

        fitnesses = divFitnessList(results, evals) # generates an average fitness over 5 games

        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Replace the current population by the offspring
        #print(tools.selBest(offspring, 1)[0])
        population[:] = offspring

        pickle.dump(population, open("Gathering Results/saves/One-Population Coevolution (no NGSA or mu lambda)/population_gen%i.p" % gen, 'wb'))

        # Append the current generation statistics to the logbook
        # record = stats.compile(population) if stats else {}
        #logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        #if verbose:
            #print (logbook.stream)

    return population

CXPB = 0.5
MUTPB = 0.2
NGEN = 100
evals = total_players // 6
hof = tools.HallOfFame(6)

if __name__ == "__main__":
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    toolbox.register("map", pool.map)

    pop = eaSimple(pop, toolbox, CXPB, MUTPB, NGEN,pool, stats, hof)