# Play six-handed poker in the console against random AI!
import old.sixhandedtournament_attempt1 as sixhandedtournament_attempt1
import SixPlayerHoldemTournament
import time

if __name__ == '__main__':
    print("Welcome to Jon's Poker Project!")
    user_input = 'play'
    #user_input = input("To begin, type 'play'")
    if user_input == 'play':
        start = time.time()
        #print('Playing six-handed poker with 5 other players...')
        for i in range(1):
            t = SixPlayerHoldemTournament.Tournament(False, 10, 100, evolve=False)
            #t.assign_rand_strat()
            t.begin()
            print(t.get_chip_counts())
        end = time.time()
        print('Time elapsed: %f seconds.' % (end - start))
