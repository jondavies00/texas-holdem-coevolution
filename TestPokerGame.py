import ParetoSixPlayerPoker as pspp
import time

### Poker test file for generating data to prove that my 'tag' players beat the 'random' ones

g = pspp.Game('testrandvstag', 4, 100)
t1 = time.time()
g.begin()
t2 = time.time()
print(g.get_chip_counts())
print(g.win_loss_matrix)
print("Time elapsed for 1000 hands: %f" % (t2 -t1))