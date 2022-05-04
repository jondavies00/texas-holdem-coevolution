#!/usr/bin/env python
# coding: utf-8

### Performs six-population pareto coevolution with deterministic crowding and hall of fame

import random
import math
import numpy as np

import sys
import sys

import multiprocessing as mp
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, r'C:\Users\jonat\OneDrive\Documents\Computer Science Degree\Year 3\Project\Implementation\poker')
import ParetoSixPlayerPoker as spp
import copy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import pickle

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

def assignToMatrix(six_indivs, indiv_matrix):
    ''' Takes a six individual matrix (6x6) and assigns the players to the relevant places in the whole matrix'''
    for row_number in range(np.shape(indiv_matrix)[1]):
        for i in range(np.shape(indiv_matrix)[0]):
            player = six_indivs[row_number]
            target = six_indivs[i]
            if i != row_number:
                PARETO_MATRIX[player.id-1][target.id-1] = indiv_matrix[row_number][i]
    
def paretoDominates(player, target):
    '''Returns true if the player pareto dominates the target'''
    dominating = True
    while dominating:
        # keep looping whilst player is doing better than target against every other player
        player_perf = PARETO_MATRIX[player.id]
        target_perf = PARETO_MATRIX[target.id]
        for i in range(len(player_perf)):
            # loop through the row and compare values, skipping each other and themselves
            if player.id == i or target.id == i or player.id == target.id:
                pass
            else:
                if player_perf[i] < target_perf[i] - 100:
                    dominating = False 
                    break
        return dominating
    return dominating
                    
def checkParetoDominance(population, p_no):
    # check one population's pareto dominances by counting the number of them
    dominances = {}
    # check every individual in the population
    for i in population:
        dominances[i.id]=0
        #now check every individual in the other 5 populations
        for curr_p_no,p in enumerate(populations):
            if p_no != curr_p_no:
                for target_i in p:
                    if paretoDominates(i, target_i):
                        if i.id not in dominances:
                            dominances[i.id] = 1
                        else:
                            dominances[i.id] += 1
    return dominances

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

max_hands = 200 # Maximum amount of hands to play for evaluation

def playPopulation(individuals, max_hands=max_hands):
    '''
    Takes six whole populations of individuals, plays a game of six random players from each population and returns a list 
    of tuples (indivs and matrix)
    '''
    indivs = copy.deepcopy(individuals)
    indivs_refer = []
    indivs_and_matrix = []
    for i in range(len(indivs)):
        indivs_refer.append(list(range(len(indivs[i]))))
    
    f1, f2, f3, f4, f5, f6 = [0]*len(indivs[0]),[0]*len(indivs[1]),[0]*len(indivs[2]),[0]*len(indivs[3]),[0]*len(indivs[4]),[0]*len(indivs[5])
    fitnesses = [f1,f2,f3,f4,f5,f6] 
    finished = False
    #create as many groups of 6 as poss
    while not finished:
        #print("notfinished")
        playing = []
        oppIndexes = []
        game = spp.Game('evolve', small_blind=2, max_hands=max_hands)
        for i in range(6):
            if len(indivs_refer[i]) == 0:
                # pick from whole population instead
                oppIndex=random.randint(0, players_per_pop-1)
                to_play = populations[i][oppIndex]
            else:
                oppIndex=indivs_refer[i][random.randint(0, len(indivs_refer[i])-1)] # Take a random opponent from each population that do not yet have a fitness
                to_play = indivs[i][oppIndex]
                indivs_refer[i].remove(oppIndex)
                oppIndexes.append((oppIndex, to_play.id-1))
            game.assign_network_weights(to_play[:PREFLOP_SIZE], to_play[PREFLOP_SIZE:], i)
            playing.append(to_play)
        game.begin()
        matrix = game.win_loss_matrix
        indivs_and_matrix.append((playing, matrix))
        #assignToMatrix(playing, matrix)
        #print(1)
        finished = all([len(p)==0 for p in indivs_refer])
    #print(PARETO_MATRIX)
    return indivs_and_matrix

def applyDeterministicCrowding(parents, offspring):
    new_pop = []
    #get pairs of most similar 
    paired = getSimilar(parents, offspring)
    for i in range(len(paired)):
        if paretoDominates(paired[i][0],paired[i][1]):
            # if parent pareto dominates child
            new_pop.append(paired[i][0])
        else:
            new_pop.append(paired[i][1])
    return new_pop

def getSimilar(parents, offspring):
    highest_similarity = math.inf
    similar_parent_index = -1
    similar_offspring_index = -1
    # sort parents and offspring according to the sum of their weights
    sorted_parents = sorted(parents, key=sum)
    sorted_offspring = sorted(offspring, key=sum)
    return list(zip(sorted_parents, sorted_offspring))

    pass

def getSimilarity(parent, offspring):
    # check similarity
    current_similarity = 0
    for i in range(IND_SIZE):
        current_similarity += (abs(parent[i] - offspring[i]))
    return current_similarity

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

def evaluateHardcoded(indiv,max_hands):
    '''
    Take one individual and return how they do after 1000 played hands
    '''
    game = spp.Game('evaluate-hardcoded', small_blind=2, max_hands=max_hands)
    game.assign_network_weights(indiv[:PREFLOP_SIZE], indiv[PREFLOP_SIZE:], 0)
    game.begin()
    fits = game.get_player_chip_count(0)
    f = fits
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

def evaluatePlayer(indiv):
    '''Simply return the row of the player in the caclulated pareto matrix as a tuple'''
    return tuple(PARETO_MATRIX[indiv.id])

total_players = 300 # Must be a multiple of 6
creator.create("FitnessMax", base.Fitness, weights=(1.0,)*total_players)
creator.create("Individual", list, fitness=creator.FitnessMax, id=None)

def initIndividual(weights, id):
    ind = weights(random.uniform(-1.0, 1.0) for _ in range(IND_SIZE))
    ind.id = id
    return ind

toolbox = base.Toolbox()

toolbox.register("individual", initIndividual, creator.Individual,
                id=None)
toolbox.register("evaluate", evaluatePlayer)

evolvedIndiv = pickle.load(open("Gathering Results/saves/Adapted Hardcoded Strategy/p1.p", 'rb'))

toolbox.register("select", tools.selNSGA2)

toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.2, indpb=0.05)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxOnePoint)

def initPopulation(inds, ind_init, size, ids):
    return inds(ind_init(id = ids*players_per_pop + i) for i in range(size))

toolbox.register("population", initPopulation, list, toolbox.individual, size=1, ids=None)

to_add = total_players // 2

evals = 10

players_per_pop = (total_players // 2) // 6

PARETO_MATRIX = np.zeros((total_players, total_players))

#Create 6 populations of 20 players with relevant ids
pop1 = toolbox.population(size=players_per_pop, ids=0)
pop2 = toolbox.population(size=players_per_pop, ids=1)
pop3 = toolbox.population(size=players_per_pop, ids=2)
pop4 = toolbox.population(size=players_per_pop, ids=3)
pop5 = toolbox.population(size=players_per_pop, ids=4)
pop6 = toolbox.population(size=players_per_pop, ids=5)
populations = [pop1,pop2,pop3,pop4,pop5,pop6]

for p in populations:
    for i in range(to_add // 6):
        p.append(evolvedIndiv)

logbook = tools.Logbook()
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

def eaMuPlusLambda(population, toolbox, mu, lambda_, cxpb, mutpb, ngen, stats=None,
             halloffame=None, verbose=__debug__):
             
    obj_log = tools.Logbook()
    obj_log.header = ['gen', 'nevals'] + (stats.fields if stats else [])
    logbooks = [tools.Logbook(),tools.Logbook(),tools.Logbook(),tools.Logbook(),tools.Logbook(),tools.Logbook()]
    for logbook in logbooks:
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = []
    for p in population:
        invalid_ind.append([ind for ind in p if not ind.fitness.valid])

    results = []
    async_results = []

    while len(results) < total_players: # play as many games in the population as there are players, so that everyone has a chance to play everyone else
        with mp.Pool(mp.cpu_count()) as pool:
            async_results.append(pool.apply_async(playPopulation, (invalid_ind,max_hands)))
            pool.close()
            pool.join()
        results += async_results[0].get()

    for t in results:
        assignToMatrix(t[0],t[1])

    fitnesses = []
    for i in invalid_ind:
        fitnesses.append(toolbox.map(toolbox.evaluate, i))

    for i in range(6):
        for ind, fit in zip(invalid_ind[i], fitnesses[i]):
            ind.fitness.values = fit

    # Begin the generational process
    for gen in range(1, ngen + 1):
        print("GEN: %i" % gen)
        fitnesses = []
        

        offspring = [algorithms.varOr(p, toolbox,lambda_, cxpb, mutpb) for p in population]

        # Put some random members of the hof into the offspring
        if len(hof) != 0:
            for i in range(SELECT_FROM_HOF * 6):
                offspring[random.randint(0, 5)].append(tools.selRandom(hof, 1)[0])

        # Evaluate the individuals with an invalid fitness
        invalid_ind = []
        for p in offspring:
            invalid_ind.append([ind for ind in p if not ind.fitness.valid])
        
        results = []
        async_results = []
        while len(results) < total_players: # play as many games in the population as there are players, so that everyone has a chance to play everyone else
            with mp.Pool(mp.cpu_count()) as pool:
                async_results.append(pool.apply_async(playPopulation, (invalid_ind,max_hands)))
                pool.close()
                pool.join()
            results += async_results[0].get()
            print(len(results))

        for t in results:
            assignToMatrix(t[0],t[1])

        for i in invalid_ind:
            fitnesses.append(toolbox.map(toolbox.evaluate, i))

        for i in range(6):
            for ind, fit in zip(invalid_ind[i], fitnesses[i]):
                ind.fitness.values = fit
        
        for i,o in enumerate(offspring):
            offspring[i] = applyDeterministicCrowding(population[i], o) 
            
        # Replace the current population by the offspring
        for i in range(6):
            population[i][:] = toolbox.select(population[i] + offspring[i], mu)
        
        for i,p in enumerate(population):
            pickle.dump(p, open("Gathering Results/saves/Six-Population Pareto Coevolution HOF and DC/Attempt 5 (120 per pop half seeded)/population%i_gen%i.p" % (i, gen), 'wb'))

        for p in population:
            hof.update(p)

CXPB = 0.5
MUTPB = 0.2
NGEN = 100
MU = 300
LAMBDA = 600


# The hall of fame will be limited to
hof = tools.ParetoFront()
SELECT_FROM_HOF = 20
if __name__ == "__main__":
    #pool = multiprocessing.Pool(processes=5)
    #toolbox.register("map", pool.map)
    

    eaMuPlusLambda(populations, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats, hof)



