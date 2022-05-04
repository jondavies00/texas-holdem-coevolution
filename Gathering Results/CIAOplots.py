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
import numpy as np

# Evolutionary functions and variables taken from evolution files

toolbox = base.Toolbox()

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax, id=None)

def initIndividual(weights, id):
    ind = weights(random.uniform(-1.0, 1.0) for _ in range(IND_SIZE))
    ind.id = id
    return ind

toolbox = base.Toolbox()

toolbox.register("individual", initIndividual, creator.Individual,
                id=None)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def initPopulation(inds, ind_init, size, ids):
    return inds(ind_init(id = i) for i in range(size))

toolbox.register("population", initPopulation, list, toolbox.individual, size=1, ids=None)

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

# Definitions for evaluation

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
    im.save("plots/sixpop_pareto_ngsa_hof_dc/%s.png" % fileName)

def gatherDataOnePop(gens, file_loc):
    ''' 
    This function plays the best player in each population against the best player in the previous generation's population.
    For the first generation
    '''
    evals = 1
    pop_data = []
    for i in range(1, gens+1):
        pop_data.append(pickle.load(open(file_loc + "/population_gen%i.p" % i, 'rb'))) 
    chip_data = []
    prev_opponents = [] # will be a list of 5 indiv lists
    for g,p in enumerate(pop_data):
        print(g)
        best = tools.selBest(p, 1)[0]
        # play against ancestors first
        if len(prev_opponents) != 0:
            for old_opps in prev_opponents:
                temp_data = 0
                for i in range(evals):
                    game = spp.Game('evolve', 2, 200)
                    for old in old_opps:
                        game.assign_network_weights(old[:PREFLOP_SIZE], old[PREFLOP_SIZE:], i)
                    game.assign_network_weights(best[:PREFLOP_SIZE], best[PREFLOP_SIZE:], 0)
                    game.begin()
                    temp_data +=game.get_player_chip_count(0)
                chip_data.append(temp_data)
        # now play against new generation
        
        opps = tools.selBest(pop_data[g], 5)
        temp_data = 0
        for i in range(evals):
            game = spp.Game('evolve', 2, 200)
            for i,o in enumerate(opps):
                game.assign_network_weights(o[:PREFLOP_SIZE], o[PREFLOP_SIZE:], i)
            
            game.assign_network_weights(best[:PREFLOP_SIZE], best[PREFLOP_SIZE:], 0)
            game.begin()
            temp_data += game.get_player_chip_count(0)
        chip_data.append(temp_data/evals)

        prev_opponents.append(opps)
    return chip_data

def gatherDataSixPop(gens, pop, file_loc):
    ''' 
    This function plays the best player in the first population against the best players in the previous generation's populations.
    '''
    pops_data = []

    for i in range(1, gens+1):
        for p in range(6):
            pops_data.append(pickle.load(open(file_loc + "/population%i_gen%i.p" % (p, i), 'rb'))) 

    chip_data = []
    prev_opponents = [] # will be a list of 5 indiv lists
    
    for g in range(gens):
        best = tools.selBest(pops_data[(g*6) + pop], 1)[0] # best from pop 1
        print((g*6) + pop)
        # play against ancestors first
        if len(prev_opponents) != 0:
            for old_opps in prev_opponents:
                game = spp.Game('evolve', 2, 200)
                for old in old_opps:
                    game.assign_network_weights(old[:PREFLOP_SIZE], old[PREFLOP_SIZE:], i)
                game.assign_network_weights(best[:PREFLOP_SIZE], best[PREFLOP_SIZE:], 0)
                game.begin()
                chip_data.append(game.get_player_chip_count(p))
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
        chip_data.append(game.get_player_chip_count(pop))
    return chip_data

def plotObjFitnessSixPop(gens, file_loc, pop, fn):
    evals = 100
    pop_data = []
    for i in range(1, gens+1):
        pop_data.append(pickle.load(open(file_loc + "population%i_gen%i.p" % (pop,i), 'rb'))) 
    chip_data = []
    for g,p in enumerate(pop_data):
        mean_chips = 0
        print(g)
        best = tools.selBest(pop_data[g], 1)[0]
        for i in range(evals):
            game = spp.Game('rand', 2, 200)
            game.assign_network_weights(best[:PREFLOP_SIZE], best[PREFLOP_SIZE:], 0)
            game.begin()
            mean_chips += game.get_player_chip_count(0)
        chip_data.append((mean_chips/evals) - 1000)
    plt.plot(range(gens), chip_data)
    plt.xlabel("Generations")
    plt.ylabel("Avg fitness from 100 games")
    plt.title("Average Fitness over 100 generations against a random strategy")
    plt.savefig("plots/" + fn + ".png")
    return chip_data

def plotObjFitnessOnePop(gens, file_loc, fn):
    evals = 100
    pop_data = []
    for i in range(1, gens+1):
        pop_data.append(pickle.load(open(file_loc + "population_gen%i.p" % i, 'rb'))) 
    chip_data = []
    for g,p in enumerate(pop_data):
        mean_chips = 0
        print(g)
        best = tools.selBest(pop_data[g], 1)[0]
        for i in range(evals):
            game = spp.Game('rand', 2, 200)
            game.assign_network_weights(best[:PREFLOP_SIZE], best[PREFLOP_SIZE:], 0)
            game.begin()
            mean_chips += game.get_player_chip_count(0)
        chip_data.append((mean_chips/evals) - 1000)
    plt.plot(range(gens), chip_data)
    plt.xlabel("Generations")
    plt.ylabel("Avg fitness from 100 games")
    plt.title("Average Fitness over 100 generations against a random strategy")
    plt.savefig("plots/" + fn + ".png")
    return chip_data

def plotAvgPopFitness(gens, file_loc, fn, type, evals=1, pop=None):
    '''
    Records the average fitnesses vs the specified type in the specified population. If its a single population, then pop will be ignored.
    '''
    if type == "easy":
        eval_type = "evaluate-lag"
    elif type == "hard":
        eval_type = "evaluate-tag"
    elif type == "rand":
        eval_type = "rand"
    else:
        raise ValueError("Invalid evaluation type.")
    if pop != None:
        six_pop = True
    else:
        six_pop = False
    pop_data = []
    for i in range(1, gens+1):
        if six_pop:
            pop_data.append(pickle.load(open(file_loc + "population%i_gen%i.p" % (pop,i), 'rb'))) 
        else:
            pop_data.append(pickle.load(open(file_loc + "population_gen%i.p" % i, 'rb'))) 
    gen_data = []
    all_data = []
    for i,g in enumerate(pop_data):
        mean_chips = 0
        print("Gen: " , i)
        gen_data = []
        for ind in g:
            mean_chips = 0
            for i in range(evals):
                game = spp.Game(eval_type, 2, 200)
                game.assign_network_weights(ind[:PREFLOP_SIZE], ind[PREFLOP_SIZE:], 0)
                game.begin()
                mean_chips += game.get_player_chip_count(0)
            gen_data.append((mean_chips/evals) - 1000)
        all_data.append(gen_data)
    pickle.dump(all_data, open("fitnesses/" + fn + ".p", 'wb'))
    
def getCIAOPlotsSixPop(file_location, gens, CIAO_name):
    '''
    Generates an image of the CIAO plot for the given generational data for six populations.
    '''
    for i in range(6):
        fitness_data = gatherDataSixPop(gens, i, file_location)
        pixel_data = normalisedFitness(fitness_data)
        generateImage(pixel_data, gens, CIAO_name + str(i))

def getCIAOPlotsOnePop(file_location, gens, CIAO_name):
    '''
    Generates an image of the CIAO plot for the given generational data for one population.
    '''
    fitness_data = gatherDataOnePop(gens, file_location)
    pixel_data = normalisedFitness(fitness_data)
    generateImage(pixel_data, gens, CIAO_name)

def plotData(fn, save_fn, pops):
    '''
    Saves a graph of the mean fitnesses of each method throughout the generations
    '''
    all_gens_data = []
    all_gens_data.append(pickle.load(open(fn + "fitnessvseasy.p", 'rb')))
    all_gens_data.append(pickle.load(open(fn + "fitnessvshard.p", 'rb')))
    all_gens_data.append(pickle.load(open(fn + "fitnessvsrand.p", 'rb')))
    plot_data = [[],[],[]]
    max_ave_fitness = -10000
    min_ave_fitness = 10000
    for i in range(3):
        for g in all_gens_data[i]:
            plot_data[i].append(np.mean(g))
            if np.mean(g) > max_ave_fitness:
                max_ave_fitness = np.mean(g)
            if np.mean(g) < min_ave_fitness:
                min_ave_fitness = np.mean(g)
        plt.plot(range(len(plot_data[i])), plot_data[i])
    if pops == 1:
        title = "Average fitness over generations"
    else:
        title = "Average fitness over generations in population 1"
    plt.legend(["fitness vs easy", "fitness vs hard", "fitness vs random"])
    plt.xlabel("Generation")
    plt.ylabel("Average Fitness")
    plt.title(title)
    plt.savefig("Gathering Results/plots/fitness plots/" + save_fn + ".png")
    print("MAX FITNESS: %i MIN FITNESS: %i" % (max_ave_fitness, min_ave_fitness))
    #plt.show()
def plotEvolvedvsHardcoded():
    evolvedIndiv = pickle.load(open("Gathering Results/saves/Adapted Hardcoded Strategy/p1.p", 'rb'))
    times = 100
    evals = 5
    gen_data = []
    mean_chips = 0
    p2_data = []
    p3_data = []
    p4_data = []
    p5_data = []
    p6_data = []
    for i in range(times):
        print(i)
        mean_chips = 0
        m2, m3, m4, m5, m6 = 0, 0, 0, 0, 0
        for e in range(evals):
            game = spp.Game("evaluate-tag", 2, 200)
            game.assign_network_weights(evolvedIndiv[:PREFLOP_SIZE], evolvedIndiv[PREFLOP_SIZE:], 0)
            game.begin()
            mean_chips += game.get_player_chip_count(0)
            m2+=game.get_player_chip_count(1)
            m3+=game.get_player_chip_count(2)
            m4+=game.get_player_chip_count(3)
            m5+=game.get_player_chip_count(4)
            m6+=game.get_player_chip_count(5)
        gen_data.append((mean_chips/ evals) - 1000)
        p2_data.append((m2/ evals) - 1000)
        p3_data.append((m3/ evals) - 1000)
        p4_data.append((m4/ evals) - 1000)
        p5_data.append((m5/ evals) - 1000)
        p6_data.append((m6/ evals) - 1000)
        

    plt.plot(range(times), gen_data)
    plt.plot(range(times), p2_data)
    plt.plot(range(times), p3_data)
    plt.plot(range(times), p4_data)
    plt.plot(range(times), p5_data)
    plt.plot(range(times), p6_data)
    plt.legend(["Evolved Individual", "TAG 1", "TAG 2", "TAG 3", "TAG 4", "TAG 5"])
    plt.xlabel("Times ran")
    plt.ylabel("Mean chips after 5 games")
    plt.title("Average results of the evolved strategy vs the TAG (strong) strategy")
    plt.savefig("Gathering Results/plots/fitness plots/" + "evolvedindiv" + ".png")
#getCIAOPlotsOnePop("saves/One-Population Coevolution with NGSA and Mu+Lambda and deterministic crowding and HOF/Attempt 2 (all seeded)", 100, "CIAO One Pop NGSA ML Seeded")
# print("One pop reg")
# plotAvgPopFitness(100, "saves/One-Population Coevolution (no NGSA or mu lambda)/", "1PRegfitnessvshard", "hard")
# plotAvgPopFitness(100, "saves/One-Population Coevolution (no NGSA or mu lambda)/", "1PRegfitnessvseasy", "easy")
# plotAvgPopFitness(100, "saves/One-Population Coevolution (no NGSA or mu lambda)/", "1PRegfitnessvsrand", "rand")
# print("One pop NGSA and ML")
# plotAvgPopFitness(100, "saves/One-Population Coevolution with NGSA and Mu+Lambda/Attempt 1 (seeded)/", "1PPfitnessvshard", "hard")
# plotAvgPopFitness(100, "saves/One-Population Coevolution with NGSA and Mu+Lambda/Attempt 1 (seeded)/", "1PPfitnessvseasy", "easy")
# plotAvgPopFitness(100, "saves/One-Population Coevolution with NGSA and Mu+Lambda/Attempt 1 (seeded)/", "1PPfitnessvsrand", "rand")

# print("Six pop reg")
# plotAvgPopFitness(100, "saves/Six-Population Reg Coevolution/", "6PRegfitnessvshard", "hard", pop=0)
# plotAvgPopFitness(100, "saves/Six-Population Reg Coevolution/", "6PRegfitnessvseasy", "easy", pop=0)
# plotAvgPopFitness(100, "saves/Six-Population Reg Coevolution/", "6PRegfitnessvsrand", "rand", pop=0)
# print("Six pop NGSA and ML")
# plotAvgPopFitness(100, "saves/Six-Population Pareto Coevolution NGSA/Attempt 2 (using)/", "6PPfitnessvshard", "hard", pop=0)
# plotAvgPopFitness(100, "saves/Six-Population Pareto Coevolution NGSA/Attempt 2 (using)/", "6PPfitnessvseasy", "easy", pop=0)
# plotAvgPopFitness(100, "saves/Six-Population Pareto Coevolution NGSA/Attempt 2 (using)/", "6PPfitnessvsrand", "rand", pop=0)
#plotData("Gathering Results/fitnesses/6PHOFDC", "6PHOFDCfitnessvsall", 6)
#plotData("Gathering Results/fitnesses/6PPfitnessvseasy.p", "6PPfitnessvseasy")
#plotData("Gathering Results/fitnesses/6PPfitnessvsrand.p", "6PPfitnessvsrand")
#getCIAOPlotsSixPop("saves/Six-Population Reg Coevolution", 100, "CIAO Six Pop Regular")
# plotEvolvedvsHardcoded()
getCIAOPlotsOnePop("saves/One-Population Coevolution with NGSA and Mu+Lambda/Attempt 2 (not seeded)/", 100, "CIAO One Pop NGSA ML")