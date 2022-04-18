import pickle
import matplotlib.pyplot as plt
logbook = pickle.load(open("saves/Adapted Hardcoded Strategy/avg_fitness.p", "rb"))

avgs = logbook.select("avg")

plt.plot(range(101), avgs, c="black")
plt.title("Average fitness against 5 harcoded strategies")
plt.xlabel("Generation")
plt.ylabel("Average Fitness")
plt.show()