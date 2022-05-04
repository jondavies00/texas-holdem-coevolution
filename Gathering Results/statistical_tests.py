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

import scipy.stats as st

# One-population
PN1_REG_DATA = pickle.load(open("Gathering Results/fitnesses/1PRegfitnessvseasy.p", 'rb'))
PN1_PARETO_DATA = pickle.load(open("Gathering Results/fitnesses/1PPfitnessvseasy.p", 'rb'))
PN1_HOFDC_DATA = pickle.load(open("Gathering Results/fitnesses/1PHOFDCfitnessvseasy.p", 'rb'))
pn1_reg_means = []
pn1_pareto_means = []
pn1_hofdc_means = []
for i in range(100):
    pn1_reg_means.append(np.mean(PN1_REG_DATA[i]))
    pn1_pareto_means.append(np.mean(PN1_PARETO_DATA[i]))
    pn1_hofdc_means.append(np.mean(PN1_HOFDC_DATA[i]))
print("Variance for one-population single-objective coevolution: ", np.var(pn1_reg_means))
print("Variance for one-population multi-objective coevolution: ", np.var(pn1_pareto_means))
print("Variance for one-population multi-objective coevolution with HOF and DC: ", np.var(pn1_hofdc_means))
print("Normal test for one-population single-objective coevolution: ",st.normaltest(pn1_reg_means))
print("Normal test for one-population multi-objective coevolution: ",st.normaltest(pn1_pareto_means))
print("Normal test for one-population multi-objective coevolution with HOF and DC: ",st.normaltest(pn1_hofdc_means))

# Data not normal, and variances different, so Mann-Whitney U
print(st.mannwhitneyu(pn1_reg_means, pn1_pareto_means))
print(st.mannwhitneyu(pn1_pareto_means, pn1_hofdc_means))


# Six-population
PN6_REG_DATA = pickle.load(open("Gathering Results/fitnesses/6PRegfitnessvseasy.p", 'rb'))
PN6_PARETO_DATA = pickle.load(open("Gathering Results/fitnesses/6PPfitnessvseasy.p", 'rb'))
PN6_HOFDC_DATA = pickle.load(open("Gathering Results/fitnesses/6PHOFDCfitnessvseasy.p", 'rb'))
pn6_reg_means = []
pn6_pareto_means = []
pn6_hofdc_means = []
for i in range(100):
    pn6_reg_means.append(np.mean(PN6_REG_DATA[i]))
    pn6_pareto_means.append(np.mean(PN6_PARETO_DATA[i]))
    pn6_hofdc_means.append(np.mean(PN6_HOFDC_DATA[i]))
print("Variance for six-population single-objective coevolution: ", np.var(pn6_reg_means))
print("Variance for six-population multi-objective coevolution: ", np.var(pn6_pareto_means))
print("Variance for six-population multi-objective coevolution with HOF and DC: ", np.var(pn6_hofdc_means))
print("Normal test for six-population single-objective coevolution: ",st.normaltest(pn6_reg_means))
print("Normal test for six-population multi-objective coevolution: ",st.normaltest(pn6_pareto_means))
print("Normal test for six-population multi-objective coevolution with HOF and DC: ",st.normaltest(pn6_hofdc_means))

# Data not normal, and variances different, so Mann-Whitney U
print(st.mannwhitneyu(pn6_reg_means, pn6_pareto_means))
print(st.mannwhitneyu(pn6_pareto_means, pn6_hofdc_means))