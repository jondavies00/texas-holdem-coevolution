
from poker import Hand, Card, Rank, Combo, Suit
import random
from itertools import cycle

from old.test import get_flush

score_to_rank = {1:'high card', 2:'pair', 3:'two pair', 4:'three of a kind', 5:'straight', 6:'flush', 7:'full house', 8:'four of a kind', 9:'straight flush', 10:'royal flush'}

class Game():
    def __init__(self):
        p1, p2, p3, p4, p5, p6 = Player('Player 1'), Player('Player 2'), Player('Player 3'), Player('Player 4'), Player('Player 5'), Player('Player 6')
        self.players = [p1, p2, p3, p4, p5, p6]
        self.players_in_hand = []
        random.shuffle(self.players)
        self.player_pool = cycle(self.players)
        self.deck = list(Card)
        self.pot = 0
        self.bb = 10
        self.sb = 5
        self.tournament_over = False
        self.hand_count = -1
        self.community_cards = []

    def begin_action(self):
        self.pot = 0
        self.deck = list(Card)
        self.hand_count += 1
        self.new_hand()
        self.populate_player_pool()
        
    
        if self.hand_count != 0:
            for i in range(self.hand_count-1 % 6):
                next(self.player_pool)
        dealer = next(self.player_pool)
        dealer.position = 'Dealer'
        
        smb = next(self.player_pool)
        smb.position = 'Small blind'
        self.pot += smb.add_to_pot(self.sb)
        bigb = next(self.player_pool)
        bigb.position = 'Big blind'
        self.pot += bigb.add_to_pot(self.bb)
        utg = next(self.player_pool)
        utg.position = 'UTG'
        utg1 = next(self.player_pool)
        utg1.position = 'UTG + 1'
        cutoff = next(self.player_pool)
        cutoff.position = 'Cutoff'

        print('Shuffling')
        random.shuffle(self.deck)
        print('Dealing')
        for i in range(6):

            to_deal = next(self.player_pool)
            to_deal.deal(self.deck.pop(), self.deck.pop())
            print(to_deal.name + ' is ' + to_deal.position + ', dealt: ' + str(to_deal.hand), end='')

            
            print('')
        for i in range(3):
            next(self.player_pool)
        print('Beginning action. Pot = ' + str(self.pot))
        #preflop
        self.action_loop(True)
        self.populate_player_pool()
        if len(self.players_in_hand) == 1:
            self.hand_won(self.players_in_hand[0])
            self.begin_action()
        elif self.tournament_over:
            pass
        else:
            self.begin_round_stages('FLOP')

    def begin_round_stages(self, round):
        if round == 'FLOP':
            next_round = 'TURN'
        elif round == 'TURN':
            next_round = 'RIVER'
        else:
            next_round = 'SHOWDOWN'

        if round == 'SHOWDOWN':
            print(round)
            p_left = [p for p in self.players if not p.out]

            winners, score = self.showdown(p_left)
            if len(winners) == 1:
                print('%s wins with hand: %s' % (winners[0].name, score_to_rank[score]))
            else:
                print('chop pot!')
                print(winners)
        else:
            print('')
            print('%s: ' % round, end='')
            if round == 'FLOP':
                self.community_cards = [self.deck.pop() for __ in range(3)]
            else:
                self.community_cards.append(self.deck.pop())
            print(' '.join(str(c) for c in self.community_cards))
            print('')
            self.action_loop()
            self.populate_player_pool()
            if len(self.players_in_hand) == 1:
                # the winner will be the next to act
                self.hand_won(self.players_in_hand[0])
                self.begin_action()
            elif self.tournament_over:
                    print('Tournament over.')
            else:
                self.begin_round_stages(next_round)

    def populate_player_pool(self):
        self.players_in_hand = []
        for p in self.players:
            p.in_pot = 0
            if not p.out or not p.out_of_tournament:
                self.players_in_hand.append(p)
        self.player_pool = cycle(self.players_in_hand)
        if self.players_in_hand[0].position == 'Dealer':
                next(self.player_pool)

    def new_hand(self):
        for p in self.players:
            if p.stack != 0:
                p.out = False

    def action_loop(self, preflop=False):
        action = (0,0)
        if preflop:
            current_bet = self.bb
        else:
            current_bet = 0
        out_of_tournament = 0
        action_left = len(self.players_in_hand)
        out = 6 - action_left
        while action_left != 0:
            to_act = next(self.player_pool)
            if not to_act.out:
                print('%s to act...' % to_act.position)
                while action[0] == 0:
                    action = to_act.get_action(current_bet, self.bb)
                if action[0] == 1:
                    #folded
                    to_act.out = True
                    action_left -= 1
                    out+=1
                elif action[0] == 2:
                    #call
                    adding_to_pot = current_bet - to_act.in_pot
                    self.pot += to_act.add_to_pot(adding_to_pot)
                    print('Call. Pot = %i' % self.pot)
                    action_left -= 1
                elif action[0] == 3:
                    #check
                    action_left -= 1
                    print('Check')
                elif action[0] == 4:
                    #bet. don't need to worry about 'in_pot' because you can only bet when there's no current bet
                    self.pot += to_act.add_to_pot(action[1])
                    current_bet = action[1]
                    print('Bet of %i. Pot = %i' % (action[1], self.pot))
                    action_left = 5 - out
                elif action[0] == 5:
                    #raise
                    adding_to_pot = action[1] - to_act.in_pot
                    self.pot += to_act.add_to_pot(adding_to_pot)
                    current_bet = adding_to_pot
                    print('Raise of %i. Pot = %i' % (action[1], self.pot))
                    action_left = 5- out
                action = (0,0)
            # else:
            #     out+=1
            #     action_left -= 1
            if out == 5:
                #check if all players are out of chips
                for player in self.players:
                    if player.stack == 0:
                        out_of_tournament += 1
                if out_of_tournament == 5:
                    winner = [p for p in self.player_pool if player.out == False]
                    self.tournament_over = True
                    print('Tournament over, winner is %s!' % winner)
                else:
                    break
        #end of round
        return out

    def hand_won(self, player):
        print('%s wins the hand' % player.position)
        player.add_to_stack(self.pot)

    def showdown(self, players):
        player_score = {}
        for p in players:
            hole_and_community = p.get_hand() + self.community_cards
            player_score[p] = self.get_highest_combo(hole_and_community)
        p_win = max(player_score, key=player_score.get)
        p_score = player_score[max(player_score, key=player_score.get)]
        # if there is more than one person with the winning hand, check for highest card
        if sum(value == p_score for value in player_score.values()) > 1:
            #list of players also with that hand
            winners = [p for p in player_score.keys() if player_score[p]==p_score]
            
            #high card
            
            current_highest = p_win
            same_hand = False
            same_handed = []
            for winner in winners:
                if p_score == 1:
                    winner.win_combo = max(winner.get_hand() + self.community_cards)
                elif p_score == 2:
                    winner.win_combo = max(self.get_x_of_a_kind(winner.get_hand() + self.community_cards, 2))
                elif p_score == 3:
                    pairs = self.get_two_pair(winner.get_hand() + self.community_cards)
                    pairs.sort()
                    pairs.reverse()
                    new_pairs =[pairs[0], pairs[1]]
                    winner.win_combo = new_pairs
                elif p_score == 4:
                    winner.win_combo = max(self.get_x_of_a_kind(winner.get_hand() + self.community_cards, 3))
                elif p_score == 5:
                    winner.win_combo = max(self.get_straight(winner.get_hand() + self.community_cards))
                elif p_score == 6:
                    winner.win_combo = max(self.get_flush(winner.get_hand() + self.community_cards))
                elif p_score == 7:
                    winner.win_combo = max(self.get_full_house(winner.get_hand() + self.community_cards))
                elif p_score == 8:
                    #foak
                    winner.win_combo = max(self.get_x_of_a_kind(winner.get_hand() + self.community_cards, 4))
                elif p_score == 9:
                    pass 
                
                if current_highest.win_combo < winner.win_combo:
                    draw = False
                    current_highest = winner
                elif current_highest.win_combo == winner.win_combo:
                    current_highest = winner
                    if winner != current_highest:
                        same_hand = True
                        same_handed.append(winner)
                    
            if same_hand:
                if p_score == 3:
                    print("!")
                #check kickers
                draw = False
                for p in same_handed:
                    check_cards = self.community_cards + p.get_hand()
                    check_ranks = []
                    for c in check_cards:
                        check_ranks.append(c.rank)
                    remove_win = [r for r in check_ranks if r != p.win_combo]
                    #remove_win = self.community_cards + p.get_hand() - p.win_combo
                    p.win_combo = max(remove_win)
                current = winners[0].win_combo
                i = 0
                index = 0
                for p in same_handed:
                    if p.win_combo > current:
                        draw = False
                        current = p.win_combo
                        index = i
                    else:
                        draw = True
                    i+=1
                if not draw:
                    return [same_handed[index]], p_score
                else:
                    return same_handed, p_score
            else:
                return [current_highest], p_score
        else:
            return [p_win], p_score

    def is_royal_flush(self, cards):
        '''
        cards: seven cards composed of community and hole cards
        '''
        rf_cards = 0
        suits = [0,0,0,0]
        if self.is_flush(cards):
            flush = get_flush(cards)
        else:
            return False
        for c in flush: #loop 7 times
            if c.is_face:
                rf_cards += 1
            elif c.rank == Rank('T'):
                rf_cards +=1
            elif c.rank == Rank('A'):
                rf_cards +=1

        if rf_cards >= 5:
            return True
        else:
            return False

    def is_x_of_a_kind(self, cards, x):
        count = 0
        ranks = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == x:
                return True
        return False

    def get_x_of_a_kind(self, cards, x):
        count = 0
        ranks = []
        pairs = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == x:
                pairs.append(r)
        return pairs

    def is_straight(self, cards):
        count = 0
        ranks = []
        straight = False
        check_ace = False
        for c in cards:
            ranks.append(c.rank)
        ranks.sort()
        for i in range(len(ranks)-1):
            if count == 3:
                check_ace = True
            if count == 4:
                straight = True
            if i == -1:
                pass
            elif Rank.difference(ranks[i], ranks[i+1]) == 1:
                count += 1
            else:
                count = 0
        if straight:
            return True
        elif check_ace:
            if ranks[0] == Rank('2') and ranks[1] == Rank('3') and ranks[2] == Rank('4') and ranks[3] == Rank('5') and ranks[6] == Rank('A'):
                #need a way to check if there is an A2345 straight
                return True
        else:
            return False

    def get_straight(self, cards):
        ranks = []
        straight = []
        count = 0
        for c in cards:
            ranks.append(c.rank)
        ranks.sort()
        for i in range(len(ranks)-1):
            if count == 3:
                check_ace = True
            elif count == 4:
                straight = True
            elif i == -1:
                pass
            elif Rank.difference(ranks[i], ranks[i+1]) == 1:
                
                if ranks[i] not in straight:
                    straight.append(ranks[i])
                straight.append(ranks[i+1])
                count += 1
            else:
                count = 0
        if check_ace:
            if ranks[0] == Rank('2') and ranks[1] == Rank('3') and ranks[2] == Rank('4') and ranks[3] == Rank('5') and ranks[6] == Rank('A'):
                straight.append(Rank('A'))
                straight.sort()

        return straight
    
    def is_flush(self, cards):
        suits = self.count_suits(cards)
        if suits[0] >= 5 or suits[1] >= 5 or suits[2] >= 5 or suits[3] >= 5:
            return True
        else:
            return False

    def count_suits(self, cards):
        suits = [0,0,0,0]
        for c in cards:
            if c.suit == Suit('h'):
                suits[0] += 1
            elif c.suit == Suit('d'):
                suits[1] += 1
            elif c.suit == Suit('s'):
                suits[2] += 1
            else:
                suits[3] += 1
        return suits

    def get_flush(self, cards):
        if self.is_flush(cards):
            suits = self.count_suits(cards)
            for i in range(5, 8):
                if i in suits:
                    suit = suits.index(i)
            if suit == 0:
                suit = Suit('h')
            elif suit == 1:
                suit = Suit('d')
            elif suit == 2:
                suit = Suit('s')
            else:
                suit = Suit('c')
            l = [c for c in cards if c.suit == suit]
            l.sort()
            return l
        else:
            raise ValueError('error: not a flush, code broken')

    def conv_suits(self, cards):
        suits = [c.suit for c in cards]
        return suits

    def conv_rankings(self, cards):
        pass

    def is_straight_flush(self, cards):
        if self.is_flush(cards) and self.is_straight(cards):
            return True
        else:
            return False

    def is_two_pair(self, cards):
        ranks = []
        pairs = 0
        seen_ranks = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == 2 and r not in seen_ranks:
                seen_ranks.append(r)
                pairs += 1
        if pairs >= 2:
            return True
        else:
            return False

    def get_two_pair(self, cards):
        ranks = []
        pairs = []
        seen_ranks = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == 2 and r not in seen_ranks:
                seen_ranks.append(r)
                pairs.append(r)
        return pairs

    def is_full_house(self, cards):
        ranks=[]
        seen_ranks = []
        seen_two = False
        seen_three = False
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == 2 and r not in seen_ranks:
                seen_two = True
                seen_ranks.append(r)
            elif ranks.count(r) == 3 and r not in seen_ranks:
                seen_three = True
                seen_ranks.append(r)
        return seen_two and seen_three

    def get_full_house(self, cards):
        ranks=[]
        seen_ranks = []
        seen_two = False
        seen_three = False
        full_house = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == 2 and r not in seen_ranks:
                seen_two = True
                seen_ranks.append(r)
                full_house.append(r)
            elif ranks.count(r) == 3 and r not in seen_ranks:
                seen_three = True
                seen_ranks.append(r)
                full_house.append(r)
        return full_house

    def get_highest_combo(self, cards):
        '''
        takes seven cards and returns a number corresponding to the poker hand ranking ()
        '''
        if self.is_royal_flush(cards):
            return 10
        elif self.is_straight_flush(cards):
            return 9
        elif self.is_x_of_a_kind(cards, 4):
            return 8
        elif self.is_full_house(cards):
            return 7
        elif self.is_flush(cards):
            return 6
        elif self.is_straight(cards):
            return 5
        elif self.is_x_of_a_kind(cards, 3):
            return 4
        elif self.is_two_pair(cards):
            return 3
        elif self.is_x_of_a_kind(cards, 2):
            return 2
        else:
            # high card
            return 1


class Player():

    def __init__(self, name):
        self.name = name
        self.stack = 20000
        self.hand = None
        self.position = None
        self.out = False
        self.in_pot = 0
        self.win_combo = None
        self.out_of_tournament = False

    def position(self, p):
        self.position = p

    def deal(self, c1, c2):
        #Combos can be compared
        self.hand = Combo.from_cards(c1, c2)

    def get_action(self, current_bet, min_bet):
        # 1 = fold, 2 = call, 3 = check, 4= bet, 5 = raise
        #manual
        #a = (input('Action? ')).split(' ')
        #auto random
        bet_amount = random.randint(min_bet, min_bet * 3)
        if bet_amount > self.stack:
            bet_amount = self.stack
        raise_amount = random.randint(current_bet*2, current_bet*3)
        if raise_amount > self.stack:
            raise_amount = self.stack
        actionint = random.randint(1, 4)
        if actionint == 3:
            a = 'bet ' + str(bet_amount)
        elif actionint == 4:
            a = 'raise ' + str(raise_amount)
        elif actionint == 1:
            a = 'fold'
        elif actionint == 2:
            a = 'call'
        a = a.split(' ')
        if len(a) > 1:
            a[1] = int(a[1])
        if a[0] == 'fold':
            return (1, 0)
        elif a[0] == 'call':
            if current_bet == 0:
                #print('Cannot call, must check or bet')
                return (0,0)
            elif current_bet == self.in_pot:
                #print('Cannot call zero chips, check instead')
                return (0,0)
            else:
                return (2, 0)
        
        elif a[0] == 'check':
            if current_bet > 0 and current_bet != self.in_pot:
                #print('Cannot check, there is a bet/raise')
                return (0,0)
            else:
                return (3, 0)

        #if someone chose to bet
        elif a[0] == 'bet':
            if current_bet > 0:
                #print('Error: must raise')
                return (0,0)
            elif not(a[1] >= min_bet):
                #print('Error: min bet is %i' % min_bet)
                return (0,0)
            elif a[1] >= self.stack:
                #print('All in')
                return (4, self.stack)
            else:
                return (4, a[1])

        #if someone chose to raise
        elif a[0] == 'raise':
            if current_bet == 0:
                #print('Cannot raise, no current bet')
                return (0,0)
            if not(a[1] >= current_bet*2):
                #print('Error, bet must be at least double the current bet, which is %i' % current_bet)
                return (0,0)
            else:
                return (5,a[1])
        else:
            #print('Invalid action')
            return (0, 0)

    def add_to_pot(self, amount):
        self.in_pot += amount
        self.stack -= amount
        return amount

    def add_to_stack(self, amount):
        self.stack += amount

    def get_hand(self):
        c1, c2 = self.hand.first, self.hand.second
        return [c1, c2]

g = Game()
for i in range(10):
    g.begin_action()
    print('tournament over')

    # if len(p.win_combo) > 1:
    #     #do something here
    #     for r in check_ranks:
    #         if r not in p.win_combo:
    #             check_kickers.append(r)

    # remove_win = [r for r in check_ranks if r != p.win_combo]

    # for r in check_ranks:
    #     if r != p.win_combo and r not in check_kickers:
    #         check_kickers.append(r)
    # p.win_combo = max(remove_win)

# if p_score == 1:
#     current_winner = self.check_same_cards(same_handed, 4, check_kickers) #4 possible kickers for a high card (all cards the same)
# elif p_score == 2:
#     current_winner = self.check_same_cards(same_handed, 3, check_kickers) #3 possible kickers for a pair
# elif p_score == 3:
#     current_winner = self.check_same_cards(same_handed, 1, check_kickers) #1 possible kicker for a 2 pair
# elif p_score == 4 or p_score == 5 or p_score == 6:
#     current_winner = self.check_same_cards(same_handed, 2, check_kickers) #2 possible kickers for a 3oak,straight,flush
# elif p_score == 7 or p_score == 10 or p_score == 9:
#     #if players have same full house, they must draw (no kicker)
#     current_winner = same_handed
# elif p_score == 8:
#     current_winner = self.check_same_cards(same_handed, 1, check_kickers) #1 possible kicker for a 4oak
# else:
#     current_winner = self.check_same_cards(same_handed, 1, check_kickers) #otherwise 1 kicker