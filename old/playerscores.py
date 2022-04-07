from SixPlayerHoldemTournament import Tournament, Player
import matplotlib.pyplot as plt
import time
import cProfile
import multiprocessing as mp



def run_tourneys(number):
    '''
    Run a number of tournaments, and append the results to a list
    '''
    wins = {'Player 1':0, 'Player 2':0, 'Player 3':0, 'Player 4':0, 'Player 5':0, 'Player 6': 0}
    for i in range(number):
        t = Tournament(20)
        t.begin()
        w = t.get_winner()
        wins[w.name] += 1
    print(wins) 

def get_fitness(player):
    pass

def plot_tournament_chip_history(t):
    y1 = t.get_player_history('Player 1')
    y2 = t.get_player_history('Player 2')
    y3 = t.get_player_history('Player 3')
    y4 = t.get_player_history('Player 4')
    y5 = t.get_player_history('Player 5')
    y6 = t.get_player_history('Player 6')
    x = list(range(0, t.get_hand_count()))
    figure, ax = plt.subplots()
    ax.plot(x, y1)
    ax.plot(x, y2)
    ax.plot(x, y3)
    ax.plot(x, y4)
    ax.plot(x, y5)
    ax.plot(x, y6)
    ax.set_xlabel('Hand number')
    ax.set_ylabel('Player chip count')
    ax.legend(['Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5', 'Player 6'])
    plt.show(block=True)
if __name__ == '__main__':
    # start = time.time()
    # wincounts = run_tourneys(10)
    # end = time.time()
    # print('Time elapsed: %f seconds.' % (end - start))
    
    # print(wincounts)
    t = Tournament(20, 20000)
    t.begin()
    plot_tournament_chip_history(t)

    # cProfile.run('t.begin()')
    # start = time.time()
    # pool = mp.Pool(mp.cpu_count())
    # print(mp.cpu_count())
    # result = pool.map(run_tourneys, [20,20,20,20,20,20,20,20,20,20,20,20])

    # end = time.time()
    # print('Time elapsed: %f seconds.' % (end - start))

