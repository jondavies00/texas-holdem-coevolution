import random
import math
from datetime import datetime
import time
import numpy as np
import poker
import sys
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, r'C:\Users\jonat\OneDrive\Documents\Computer Science Degree\Year 3\Project\Implementation\poker')
import SixPlayerHoldemTournament as spt



# t = spt.Tournament(tournament=False, small_blind=10, max_hands=200) # Begin a 'tournament' of 200 hands. We make tournament false to not double the big blinds every 20 hands
# t.begin()



from deap import base
from deap import creator
from deap import tools



IND_SIZE = 12

creator.create("FitnessMax", base.Fitness, weights=(1.0,)) # maximise chips
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()


toolbox.register("attr_preflop1", random.randint, 0, 100)
toolbox.register("attr_preflop2", random.randint, 0, 100)
toolbox.register("attr_preflop3", random.uniform, 0, 500)
toolbox.register("attr_afterpreflop1", random.randint, 0, 10)
toolbox.register("attr_afterpreflop2", random.randint, 0, 10)
toolbox.register("attr_afterpreflop3", random.uniform, 0, 500)


toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_preflop1,toolbox.attr_preflop2,toolbox.attr_preflop3,
                 toolbox.attr_afterpreflop1,toolbox.attr_afterpreflop2,toolbox.attr_afterpreflop3,
                 toolbox.attr_afterpreflop1,toolbox.attr_afterpreflop2,toolbox.attr_afterpreflop3,
                 toolbox.attr_afterpreflop1,toolbox.attr_afterpreflop2,toolbox.attr_afterpreflop3), n=1)


def evaluate(indivs):
    start = time.time()
    t = spt.Tournament(tournament=False, small_blind=10, max_hands=100)
    # Take 6 individuals, assign their strategies to the players and run a game
    for (c,ind) in enumerate(indivs):
        #print('indiv:')
        #print(i)
        t.assign_bot_strategy(ind, c)
    start = time.time()
    t.begin()
    end = time.time()
    print('Time elapsed: %f seconds.' % (end - start))
    print('1 group of 6 evaluated')
    pc1, pc2, pc3, pc4, pc5, pc6 = [c-20000 for c in t.get_chip_counts()]
    return [pc1, pc2, pc3, pc4, pc5, pc6], #returns list of chip counts for the 6 players

def mutateCustom(indiv, indpb):
    '''
    Take an individual and mutate each 'row' of genes
    '''
    #preflop genes
    pfg1 = indiv[0] #cont
    pfg2 = indiv[1] #best
    pfg3 = indiv[2] #bet
    if random.random() < indpb:
        indiv[0] = toolbox.attr_preflop1()
        indiv[1] = toolbox.attr_preflop2()
        indiv[2] = toolbox.attr_preflop3()
        for i in range(3, 12, 3):
            indiv[i] = toolbox.attr_afterpreflop1()
            indiv[i+1] = toolbox.attr_afterpreflop2()
            indiv[i+2] = toolbox.attr_afterpreflop3()
    return indiv,

toolbox.register("evaluate", evaluate)
toolbox.register("select", tools.selTournament, tournsize=3)

toolbox.register("mutate", mutateCustom, indpb=0.1) 



toolbox.register("population", tools.initRepeat, list, toolbox.individual)



pop = toolbox.population(n=102)



logbook = tools.Logbook()
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)



start_index = 0
end_index = 6
groupings = []
for i in range(len(pop)//6):
    groupings.append(pop[start_index:end_index])
    start_index += 6
    end_index += 6

def flatten(t):
    return [item for sublist in t for item in sublist]

fitnesses = [toolbox.evaluate(g) for g in groupings]
fitnesses = flatten(flatten(fitnesses))
        
for (i,ind) in enumerate(pop):
    ind.fitness.values = (fitnesses[i],)

NGEN = 10
for g in range(NGEN):
    print("-- Generation %i --" % g)
      
    offspring = toolbox.select(pop, len(pop))
    offspring = list(map(toolbox.clone, offspring))

    for mutant in offspring:
        toolbox.mutate(mutant)
        del mutant.fitness.values
                         
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = [toolbox.evaluate(g) for g in groupings]
    fitnesses = flatten(flatten(fitnesses))
    
    for (i,ind) in enumerate(invalid_ind):
        ind.fitness.values = (fitnesses[i],)

    pop[:] = offspring
    record = stats.compile(pop)
    logbook.record(gen=g, **record)


indiv1 = tools.selBest(pop, 1)[0]
print(indiv1)



avgs = logbook.select("avg")
print(avgs)

import matplotlib.pyplot as plt
gen = logbook.select("gen")
avgs = logbook.select("avg")
stds = logbook.select("std")
plt.rc('axes', labelsize=14)
plt.rc('xtick', labelsize=14)
plt.rc('ytick', labelsize=14) 
plt.rc('legend', fontsize=14)
fig, ax1 = plt.subplots()
line1 = ax1.plot(gen, avgs)
line1 = ax1.errorbar(gen, avgs, yerr=stds, errorevery=2)
ax1.set_xlabel("Generation")
ax1.set_ylabel("Mean Fitness")


pop = toolbox.population(n=5)
pop.append(indiv1)

indiv1F, otherF = [], []
for i in range(100):
    fitnesses = toolbox.evaluate(pop)
    indiv1F.append(fitnesses[0][5])
    otherF.append(sum(fitnesses[0][0:5])/5)


plt.plot(np.arange(0,100), indiv1F)

plt.plot(np.arange(0,100),otherF)


f = toolbox.evaluate(pop)
print(f)
