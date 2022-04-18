### A CIAO plot is 'Current Individual vs Ancestral Opponents'
### To create one, we need the records of all players in a coevolution run.

### To record one for six populations, we take the best from one population and play them against the best from the other five
### We can then repeat this for each generation, and make sure to play the recent one against all of the old ones too

### This may also take processing time, but the results should allow for deeper analysis into the coevolutionary dynamics.

# Imports
import pickle
from PIL import Image
from numpy.random import randint
from deap import tools
from deap import base
from deap import creator
import random
import ParetoSixPlayerPoker as spp
import matplotlib.pyplot as plt

toolbox = base.Toolbox()
#toolbox.register("attr_float", random.uniform, -1.0, 1.0)


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

toolbox.register("population", tools.initRepeat, list, toolbox.individual)
def initPopulation(inds, ind_init, size, ids):
    return inds(ind_init(id = i) for i in range(size))

toolbox.register("population", initPopulation, list, toolbox.individual, size=1, ids=None)

# Definitions

def normalisedFitness(values):
    ''' 
    Returns a list of normalised fitness values given the values. 
    values: a list of average fitness values throughout generations
    '''
    if min(values) < 0:
        values = [v+abs(min(values)) for v in values]
    else:
        values = [v-min(values) for v in values]
    return [v/max(values) for v in values]

def generateImage(pixel_values, gens, fileName):
    '''
    Given an array of greyscale pixel values generated from fitness (from gen 1 to max), generate a CIAO plot image
    This works by going pixel by pixel from the bottom. 
    '''
    pixel_data = []
    pixel_values.reverse()
    pixel_values = [p*255 for p in pixel_values]

    group = gens
    index = 0
    count = 0
    while index != len(pixel_values):
        pixel_data += pixel_values[index:index+group] + (gens - group)*[255]
        index += group
        group -=1

    im = Image.new('L', (gens, gens))
    im.putdata(pixel_data)
    im.save("Gathering Results/plots/sixpop_pareto_ngsa/%s.png" % fileName)


# 1. Gather the data
# To start, I will need all of the best individual representations from each generation of some coevolution

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

def gatherDataOnePop(gens):
    ''' 
    This function plays the best player in each population against the best player in the previous generation's population.
    For the first generation
    '''
    pop_data = []
    for i in range(1, gens+1):
        pop_data.append(pickle.load(open("Gathering Results/saves/One-Population Coevolution with NGSA and Mu+Lambda and deterministic crowding and HOF/population_gen%i.p" % i, 'rb'))) 
    chip_data = []
    prev_opponents = [] # will be a list of 5 indiv lists
    
    for g,p in enumerate(pop_data):
        best = tools.selBest(p, 1)[0]
        # play against ancestors first
        if len(prev_opponents) != 0:
            for old_opps in prev_opponents:
                for old in old_opps:
                    game.assign_network_weights(old[:PREFLOP_SIZE], old[PREFLOP_SIZE:], i)
                game.assign_network_weights(best[:PREFLOP_SIZE], best[PREFLOP_SIZE:], 0)
                game.begin()
                chip_data.append(game.get_player_chip_count(0))
        # now play against new generation
        game = spp.Game('evolve', 2, 200)
        
        opps = tools.selBest(pop_data[g], 5)
        for i,o in enumerate(opps):
            game.assign_network_weights(o[:PREFLOP_SIZE], o[PREFLOP_SIZE:], i)
        prev_opponents.append(opps)
        game.assign_network_weights(best[:PREFLOP_SIZE], best[PREFLOP_SIZE:], 0)
        game.begin()
        chip_data.append(game.get_player_chip_count(0))
    return chip_data

def gatherDataSixPop(gens, pop):
    ''' 
    This function plays the best player in the first population against the best players in the previous generation's populations.
    '''
    pops_data = []

    for i in range(1, gens+1):
        for p in range(6):
            pops_data.append(pickle.load(open("Gathering Results/saves/Six-Population Pareto Coevolution NGSA/population%i_gen%i.p" % (p, i), 'rb'))) 

    chip_data = []
    prev_opponents = [] # will be a list of 5 indiv lists
    
    for g in range(gens):
        best = tools.selBest(pops_data[((g-1)*6) + pop], 1)[0] # best from pop 1
        # play against ancestors first
        if len(prev_opponents) != 0:
            for old_opps in prev_opponents:
                for old in old_opps:
                    game.assign_network_weights(old[:PREFLOP_SIZE], old[PREFLOP_SIZE:], i)
                game.assign_network_weights(best[:PREFLOP_SIZE], best[PREFLOP_SIZE:], 0)
                game.begin()
                chip_data.append(game.get_player_chip_count(0))
        # now play against new generation
        game = spp.Game('evolve', 2, 200)
        opps = []
        for i in range(6):
            if i != pop:
                opps.append(tools.selBest(pops_data[g*6 +i], 1)[0])
        for i,o in enumerate(opps):
            game.assign_network_weights(o[:PREFLOP_SIZE], o[PREFLOP_SIZE:], i)
        prev_opponents.append(opps)
        game.assign_network_weights(best[:PREFLOP_SIZE], best[PREFLOP_SIZE:], 0)
        game.begin()
        chip_data.append(game.get_player_chip_count(0))
    return chip_data


def plotObjFitness(gens):
    evals = 5
    pop_data = []
    for i in range(1, gens+1):
        pop_data.append(pickle.load(open("saves/One-Population Coevolution with NGSA and Mu+Lambda and deterministic crowding and HOF/population_gen%i.p" % i, 'rb'))) 
    chip_data = []
    for g,p in enumerate(pop_data):
        mean_chips = 0
        print(g)
        for i in range(evals):

            best = tools.selBest(pop_data[0], 1)[0]
            # play against ancestors first
            game = spp.Game('evolvevshardcoded', 2, 200)
            game.assign_network_weights(best[:PREFLOP_SIZE], best[PREFLOP_SIZE:], 0)
            game.begin()
            mean_chips += game.get_player_chip_count(0)
        chip_data.append((mean_chips/evals) - 1000)
    plt.plot(range(gens), chip_data)
    plt.show()
    return chip_data


# for i in range(100):
#     # i is the generation number

#     best_from_focus_population = pickle.load(("/some/directory/usefulpop1%i.p" % i), "r")
#     best_from_other_1 = pickle.load(("/some/directory/usefulpop2%i.p" % i), "r")
#     best_from_other_2 = pickle.load(("/some/directory/usefulpop3%i.p" % i), "r")
#     best_from_other_3 = pickle.load(("/some/directory/usefulpop4%i.p" % i), "r")
#     best_from_other_4 = pickle.load(("/some/directory/usefulpop5%i.p" % i), "r")
#     best_from_other_5 = pickle.load(("/some/directory/usefulpop6%i.p" % i), "r")

    # game = spp.game("evolve")
    # game.assignfitness(best) x 6
    # game.begin play x times
    # save indivs 2 to 6 {0:[indiv1,indiv2,indiv3,indiv4]}
    # get chips value from pop1 player
    # next gen, repeat the same and for last gen
    
fitness_data = gatherDataSixPop(100, 0)
pixel_data = normalisedFitness(fitness_data)
generateImage(pixel_data, 100, "CIAO1")

fitness_data = gatherDataSixPop(100, 1)
pixel_data = normalisedFitness(fitness_data)
generateImage(pixel_data, 100, "CIAO2")

fitness_data = gatherDataSixPop(100, 2)
pixel_data = normalisedFitness(fitness_data)
generateImage(pixel_data, 100, "CIAO3")

fitness_data = gatherDataSixPop(100, 3)
pixel_data = normalisedFitness(fitness_data)
generateImage(pixel_data, 100, "CIAO4")

fitness_data = gatherDataSixPop(100, 4)
pixel_data = normalisedFitness(fitness_data)
generateImage(pixel_data, 100, "CIAO5")

fitness_data = gatherDataSixPop(100, 5)
pixel_data = normalisedFitness(fitness_data)
generateImage(pixel_data, 100, "CIAO6")

# plotObjFitness(100)