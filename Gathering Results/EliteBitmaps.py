# considering my genotype information is not in bits, it will be difficult to do
# could do a plot of how far away a network weight is away from 1
# 0.9 fairly dark, 0 middle grey, -1 white
# still will show genetic change of elite individual

# or a number for the difference between one individual's weight and another's
import pickle
from PIL import Image
from numpy import indices
from numpy.random import randint
from deap import tools
from deap import base
from deap import creator
import random
import ParetoSixPlayerPoker as spp
import matplotlib.pyplot as plt

toolbox = base.Toolbox()
#toolbox.register("attr_float", random.uniform, -1.0, 1.0)

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

def calculateDifference(ind1, ind2):
    '''
    Takes two elite individuals and produces a list of how genetically similar they are. This is done by 
    taking the difference between the two. This list will then be normalised.
    '''
    return [abs(g1 - g2) for (g1,g2) in zip(ind1,ind2)]

def normalisedFitness(values):
    ''' 
    Returns a list of normalised fitness values given the values. 
    values: a list of average fitness values throughout generations
    '''
    if min(values) < 0:
        values = [v+abs(min(values)) for v in values]
    else:
        values = [v-min(values) for v in values]
    maxVal = max(values)
    if maxVal == 0:
        return [v/0.00001 for v in values]
    else:
        return [v/maxVal for v in values]
def generateEBImage(pixel_values, gens, fileName):
    '''
    Given an array of greyscale pixel values generated from fitness (from gen 1 to max), generate a CIAO plot image
    This works by going pixel by pixel from the bottom. 
    '''
    pixel_data = []
    for i in pixel_values:
        # each individual, left to right of their geno differences
        rgbVals = [255-(p*255) for p in i]
        pixel_data += rgbVals

    im = Image.new('L', (IND_SIZE, gens))
    im.putdata(pixel_data)
    im.save("Gathering Results/plots/sixpop_pareto_ngsa_hof_dc/%s.png" % fileName)

def getEliteBitmapOnePop(gens, file_loc):
    pops_data = []

    for i in range(1, gens+1):
        pops_data.append(pickle.load(open(file_loc + "/population_gen%i.p" %  i, 'rb'))) 
    geno_data = []
    currentElite = []
    formerElite = [0]*IND_SIZE
    for p in pops_data:

        currentElite = tools.selBest(p, 1)[0]

        geno_data.append(normalisedFitness(calculateDifference(currentElite, formerElite)))
        formerElite = currentElite
    return geno_data

def getEliteBitmapSixPop(gens, pop, file_loc):
    pops_data = []

    for i in range(1, gens+1):
        pops_data.append(pickle.load(open(file_loc + "/population%i_gen%i.p" %  (pop,i), 'rb'))) 
    geno_data = []
    currentElite = []
    formerElite = [0]*IND_SIZE
    for p in pops_data:

        currentElite = tools.selBest(p, 1)[0]

        geno_data.append(normalisedFitness(calculateDifference(currentElite, formerElite)))
        formerElite = currentElite
    return geno_data

# for i in range(6):

#     values = getEliteBitmap(100, i)
#     generateEBImage(values, 100, "Elite Bitmap Pop%i" % (i+1))
#a = pickle.load(open("Gathering Results/saves/One-Population Coevolution with NGSA/Attempt 2/population0_gen2.p", 'rb'))
#b = pickle.load(open("Gathering Results/saves/One-Population Coevolution with NGSA/Attempt 2/population0_gen10.p", 'rb'))
#print("")

values1 = getEliteBitmapSixPop(100,0 ,  "Gathering Results/saves/\Six-Population Pareto Coevolution NGSA/Attempt 2/")

#values2 = getEliteBitmapSixPop(100,0, "Gathering Results\saves\Six-Population Pareto Coevolution HOF and DC\Attempt 4 (50 per pop)")


generateEBImage(values1, 100, "Elite Bitmap 6Pop Pareto NGSA and ML p1")