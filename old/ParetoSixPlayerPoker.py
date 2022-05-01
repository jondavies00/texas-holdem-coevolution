
from multiprocessing.sharedctypes import Value
from typing import Type
from poker import Hand, Card, Rank, Combo, Suit, Range, hand
from random import shuffle, randint, uniform, choice
from itertools import cycle
from operator import attrgetter, truediv
import numpy as np

score_to_rank = {1:'high card', 2:'pair', 3:'two pair', 4:'three of a kind', 5:'straight', 6:'flush', 7:'full house', 8:'four of a kind', 9:'straight flush', 10:'royal flush'}
BASE_HAND_RANGE = list(Range('XX').combos)
BASE_HAND_RANGE.sort()

class Game():

    # INITIALISATION

    def __init__(self, test, small_blind, max_hands, starting_chips=1000):
        '''
        Initialise the tournament.
        bb_doubling_speed: How quickly the tournament progresses. Doubling speed of 20 = big blind doubles every 20 hands.
        starting_chips: How many poker chips each player starts with.
        '''
        self.random = False
        self.pprint = False
        p1, p2, p3, p4, p5, p6 = NeuralPlayer('Player 1'), NeuralPlayer('Player 2'), NeuralPlayer('Player 3'), NeuralPlayer('Player 4'), NeuralPlayer('Player 5'), NeuralPlayer('Player 6')
        if test == 'random':
            p1, p2, p3, p4, p5, p6 = NeuralPlayer('Player 1'), RandomPlayer('Player 2'), RandomPlayer('Player 3'), RandomPlayer('Player 4'), RandomPlayer('Player 5'), RandomPlayer('Player 6')
        elif test == 'manual':
            p1, p2, p3, p4, p5, p6 = ManualPlayer('Player 1'), NeuralPlayer('Player 2'), NeuralPlayer('Player 3'), NeuralPlayer('Player 4'), NeuralPlayer('Player 5'), NeuralPlayer('Player 6')
            self.pprint = True
            p1.manual = True
        elif test == 'poker':
            p1, p2, p3, p4, p5, p6 = RandomPlayer('Player 1'), RandomPlayer('Player 2'), RandomPlayer('Player 3'), RandomPlayer('Player 4'), RandomPlayer('Player 5'), RandomPlayer('Player 6')
            self.random = True
            self.pprint = True
        elif test == 'testvstag':
            p1, p2, p3, p4, p5, p6 = TAGPlayer('Player 1'), TAGPlayer('Player 2'), TAGPlayer('Player 3'), TAGPlayer('Player 4'), TAGPlayer('Player 5'), ManualPlayer('Player 6')
            self.pprint = True
            p6.manual = True
        elif test == 'evaluate-hardcoded':
            p1, p2, p3, p4, p5, p6 = NeuralPlayer('Player 1'), TAGPlayer('Player 2'), LAGPlayer('Player 3'), LPPlayer('Player 4'), TPPlayer('Player 5'), choice([TAGPlayer('Player 6'), LAGPlayer('Player 6'), LPPlayer('Player 6'), TPPlayer('Player 6')])
        elif test == 'testrandvstag':
            p1, p2, p3, p4, p5, p6 = TAGPlayer('Player 1'), RandomPlayer('Player 2'), RandomPlayer('Player 3'), RandomPlayer('Player 4'), RandomPlayer('Player 5'), RandomPlayer('Player 6')
        elif test == 'evolve+hardcoded':
            p1, p2, p3, p4, p5, p6 = NeuralPlayer('Player 1'), NeuralPlayer('Player 2'), NeuralPlayer('Player 3'), NeuralPlayer('Player 4'), NeuralPlayer('Player 5'), choice([TAGPlayer('Player 6'), LAGPlayer('Player 6'), LPPlayer('Player 6'), TPPlayer('Player 6')])
        self.original_players = [p1, p2, p3, p4, p5, p6]
        self.players = [p1, p2, p3, p4, p5, p6]
        self.players_in_hand, self.out_players, self.community_cards,  self.chip_history = [], [], [], []
        shuffle(self.players)
        self.table_positions = cycle(self.players)
        #self.player_pool = self.table_positions
        self.deck = list(Card)
        self.pot,self.hand_count, self.showdown_count = 0,0,0
        self.start_chips = starting_chips
        for p in self.players:
            p.stack = self.start_chips
        self.bb, self.sb = small_blind * 2, small_blind
        self.winner = None
        self.win_percents = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0}
        self.bb_doubling_speed = max_hands
        self.max_hands = max_hands

        self.win_loss_matrix = np.zeros((6,6))
    # GAME LOOPS

    def begin(self):
        '''
        Start the game loop. Carry on playing hands until the tournament is over. 
        '''
        while not self.is_tournament_over() and self.hand_count < self.max_hands:
            #new round
            
            if self.pprint: print('HAND #%i' % self.hand_count)

            # if (self.hand_count+2) % self.bb_doubling_speed == 0:
            #     self.bb *= 2
            #     self.sb = self.bb / 2
            stacktotal = 0
            for p in self.players:
                if self.pprint: print('%s has stack size of %i.' % (p.name, p.stack))
                stacktotal += p.stack
            if self.pprint: print('stack total = %i, should be %i' % (stacktotal, self.start_chips * 6))
            if stacktotal != self.start_chips * len(self.original_players):
                if self.pprint: print('error in chips')
                else: pass
            self.hand_chip_counts = {player:0 for player in self.original_players}
            self.begin_action()
            
            self.hand_count += 1

        ### When the game ends, put all players back into the player list for evaluation
        for p in self.out_players:
            if p not in self.players:
                self.players.append(p)
        if self.pprint: print("Game ended")
        if self.pprint: print(self.hand_count)

    def begin_action(self):
        '''
        Initialise the hand action, assigning positions to each player.
        '''
        positions = {1:'Dealer',2:'Small blind',3:'Big blind',4:'UTG',5:'UTG+1',6:'Cutoff'}
        self.chip_history.append(self.get_all_player_chips())
        self.pot = 0
        self.deck = list(Card)
        self.community_cards =  []
        self.reset_out_players()
        self.update_out_of_tournament_players()
        self.table_positions = cycle(self.players)

        # Cycle the position based on the number of hands played MOD 6. I.e., every sixth hand will be the original position
        if self.hand_count != 0:
            for i in range((self.hand_count % 6)):
                next(self.table_positions)
        hand_player_pool = self.table_positions

        # Set the players' positions, and add the big blind and small blind to the pot
        for i in range(1, len(self.players) + 1):
            player = next(hand_player_pool)
            player.position = positions[i]
            if player.position == 'Big blind':
                self.pot += self.bb
                player.add_to_pot(self.bb)
                self.hand_chip_counts[player] += self.bb
            elif player.position == 'Small blind':
                self.pot += self.sb
                player.add_to_pot(self.sb)
                self.hand_chip_counts[player] += self.sb

        # Shuffle the deck
        if self.pprint: print('Shuffling')
        shuffle(self.deck)

        # Now deal cards to each player
        if self.pprint: print('Dealing')
        for i in range(1, len(self.players) + 1):
            to_deal = next(hand_player_pool)
            to_deal.deal(self.deck.pop(), self.deck.pop())
            if self.pprint and not to_deal.bot: print(to_deal.name + ' is ' + to_deal.position + ', dealt: ' + str(to_deal.hand), end='')
            if self.pprint: print('')
        
        ## We've looped through each player and dealt them a card, and NEXT is now dealer, we need NEXT to be UTG
        for i in range(3):
            next(hand_player_pool)

        if self.pprint: print('Beginning action. Pot = ' + str(self.pot))

        # Begin the round stage
        self.begin_round_stages(0, hand_player_pool)

    def begin_round_stages(self, p_round, players):
        '''
        Start from pre-flop, and play until there is a showdown at the end, or just one player remains.
        Args: 
        p_round: the poker round (0 == pre-flop)
        players: the players in correct order to use
        '''
        # Assign the players who are not out of the tournament to 'players_left'
        players_left = len(self.players)
        showdown = False
        # Loop whilst not needing a showdown
        while not showdown:
            is_preflop = not bool(p_round)
            if p_round == 0:
                pass
                #preflop
                # is_preflop = True
            elif p_round == 1:
                #flop
                if self.pprint: print('FLOP: ')
                self.community_cards = [self.deck.pop() for __ in range(3)]
            elif p_round == 2 or p_round == 3:
                #turn or river
                if p_round == 2:
                    if self.pprint: print('TURN: ')
                else:
                    if self.pprint: print('RIVER: ')
                self.community_cards.append(self.deck.pop())
            else:
                showdown = True
                break
            if not is_preflop:
                if self.pprint: print('')
                if self.pprint: print('%s: ' % p_round, end='')
                if self.pprint: print(' '.join(str(c) for c in self.community_cards))
                if self.pprint: print('')

            # Call the action loop once the community cards are down
            self.action_loop(players_left, players, p_round)
            
            players_left = len([x for x in self.players if x.out == False])
            players = cycle(self.populate_player_pool(players))
            

            if players_left == 1:
                for i in range(1):
                    p_won = next(players)
                #p_won = next(players)
                self.update_chip_matrix(p_won)
                self.hand_won(p_won)
                break
            elif self.all_in_showdown(players_left):
                if p_round == 0:
                    self.community_cards.append(self.deck.pop())
                    self.community_cards.append(self.deck.pop())
                    self.community_cards.append(self.deck.pop())
                    self.community_cards.append(self.deck.pop())
                    self.community_cards.append(self.deck.pop())
                elif p_round == 1:
                    self.community_cards.append(self.deck.pop())
                    if self.pprint: print('TURN: %s' % ' '.join(str(c) for c in self.community_cards))
                    self.community_cards.append(self.deck.pop())
                    if self.pprint: print('RIVER: %s'% ' '.join(str(c) for c in self.community_cards))
                elif p_round == 2:
                    self.community_cards.append(self.deck.pop())
                    if self.pprint: print('RIVER: %s'% ' '.join(str(c) for c in self.community_cards))
                showdown = True
                break
            p_round += 1
        if self.is_tournament_over():
            pass
        elif showdown:
            self.calculate_showdown()

    def action_loop(self,players_left,players, p_round):
        '''
        The action loop is where the players' actions are requested. This loops until there is no action left (everyone has called or folded bar one player)
        '''
        if p_round == 0:
            current_bet = self.bb
        else:
            current_bet = 0
        min_bet = self.bb
        time_out = 1000
        count = 0
        action_left = players_left
        out = len(self.players) - action_left
        #print(len(self.players), action_left)
        all_in = 0
        to_return = 0
        while action_left > 0:
            player_to_act = next(players)
        
            if not player_to_act.out and player_to_act.stack > 0:
                count +=1
                if self.pprint: print('%s to act...' % player_to_act.position)
                # action_type, amount = player_to_act.get_action_type_and_amount(current_bet, p_round, self.community_cards)
                if self.random: 
                    action_type = player_to_act.getActionType(p_round==0, action_left,out, self.community_cards, self.pot, current_bet)
                    amount = 0
                elif player_to_act.manual:
                    action_type, amount = player_to_act.getActionType()
                else:
                    action_type, amount = player_to_act.getActionType(p_round, action_left, (players_left - action_left), out, self.community_cards, self.pot, current_bet)
                #amount = player_to_act.get_action_amount(action_type, min_bet, current_bet)
                #amount = 0
                #print(amount)
                if action_type == 4:
                    if player_to_act.stack < min_bet:
                        amount = player_to_act.stack
                    # elif amount < min_bet:
                    #     amount = min_bet
                    # else:
                    #     amount = min_bet
                elif action_type == 5:
                    if player_to_act.stack < current_bet * 2:
                        amount = player_to_act.stack
                    # elif amount < current_bet * 2:
                    #     amount = current_bet * 2
                    # else:
                    #     amount = current_bet * 2

                # if current_bet != 0 and amount != current_bet*2:
                #     print(action_type)
                #     print(amount)
                #     raise ValueError("bet amount is invalid")

                if action_type == 1:
                    #fold
                    player_to_act.out = True
                    action_left -=1
                    out+=1
                    #if player_to_act.evolve: player_to_act.fitness -= 0.1
                    if self.pprint: print('Fold. stack = %i' % player_to_act.stack)
                elif action_type == 2:
                    #call
                    action_left -= 1
                    amount_to_call = current_bet - player_to_act.on_table
                    if amount_to_call >= player_to_act.stack:
                        #TODO: money needs to go back to raiser if caller doesn't have enough
                        
                        to_return += current_bet - player_to_act.stack

                        player_stack = player_to_act.stack
                        player_to_act.add_to_pot(player_stack)
                        self.pot += player_stack
                        self.hand_chip_counts[player_to_act] += player_stack
                    else:
                        player_to_act.add_to_pot(amount_to_call)
                        self.pot += amount_to_call
                        self.hand_chip_counts[player_to_act] += amount_to_call
                    if self.pprint: print('Call. Pot = %i, stack = %i' % (self.pot, player_to_act.stack))
                elif action_type == 3:
                    #check
                    action_left -= 1
                    if self.pprint: print('Check. stack = %i' % player_to_act.stack)
                elif action_type == 4:
                    #bet
                    better = player_to_act
                    action_left = players_left - (out)
                    player_to_act.add_to_pot(amount)
                    current_bet = amount
                    self.pot += current_bet
                    self.hand_chip_counts[player_to_act] += current_bet
                    if self.pprint: print('Bet, size = %i, pot = %i, stack = %i' % (amount, self.pot, player_to_act.stack))
                elif action_type == 5:
                    better = player_to_act
                    #raise
                    action_left = players_left - (out)
                    # amount raiser wants to raise it to subtract what they have in the pot
                    raise_amount = amount - player_to_act.on_table
                    if raise_amount <= 0:
                        raise_amount = amount
                    self.pot += raise_amount
                    self.hand_chip_counts[player_to_act] += raise_amount
                    player_to_act.add_to_pot(raise_amount)
                    current_bet = amount
                    
                    if self.pprint: print('Raise, size %i, pot = %i, stack = %i' % (amount, self.pot, player_to_act.stack))
                else:
                    raise ValueError('invalid action')
            if player_to_act.stack == 0:
                player_to_act.all_in = True
                all_in +=1
            if players_left - all_in < 2:
                break
            if out == len(self.players) - 1:
                break
            if players_left - all_in == 1:
                #if everyone has gone all in to call bar 1 person who has enough to chips to cover, the amount they have on the table should be returned6
                better.add_to_stack(to_return)
            if count == time_out:
                break
            #print(self.pot)
        if self.pprint: print('Round over, %s players left, %i in the pot' % (str(len(self.players) - out), self.pot))

    def calculate_showdown(self):
        p_left = [p for p in self.players if not p.out]
        winners, score = self.showdown(p_left)
        for p in p_left:
            #if p not in winners and p.evolve: p.fitness -= 0.1
            p.all_in = False #reset the all_in variable
        if len(winners) == 1:
            if self.pprint: print('%s wins with hand: %s %s' % (winners[0].name, score_to_rank[score], winners[0].winning_hand))
            winners[0].stack += self.pot
            self.update_chip_matrix(winners[0])
            if winners[0].evolve: winners[0].fitness += 1
            
            for p in p_left:
                if p.stack == 0 and p != winners[0]:
                    if winners[0].evolve: winners[0].fitness -= 10
                    p.out_of_tournament = True
        else:
            # TODO: Must have a way to deal with side pots
            if self.pprint: print('chop pot!')
            each_gain = self.pot / len(p_left)
            if int(each_gain) < each_gain:
                flip_for = round(each_gain) - int(each_gain)
            else:
                flip_for = 0
            flip = randint(1, len(p_left))
            for p in winners:
                if winners.index(p) == flip:
                    p.stack += flip_for
                p.stack += int(each_gain)
                self.update_chip_matrix(winners[0])
                if winners[0].evolve: winners[0].fitness += 1
            if self.pprint: print(winners)

    def all_in_showdown(self, players_left):
            all_in = 0
            for p in self.players:
                if p.all_in:
                    all_in +=1
            if players_left - all_in < 2:
                return True
            else:
                return False

    def showdown(self, players):
        '''
        A long function that takes as input a list of players going to showdown, and returns the winning player along with their score.
        '''
        score_to_kicker = {1:4,2:3,3:1,4:2,5:0,6:4,7:0,8:1,9:0,10:0} # Maps a score to how many kickers at most need to be checked
        player_score = {}
        if len(players) == 0:
            raise ValueError('No players given for showdown')
        
        for p in players:
            hole_and_community = p.get_hand() + self.community_cards
            player_score[p] = self.get_highest_combo(hole_and_community) # Map the player to their (best) made hand
            self.showdown_count +=1
            p_score = player_score[p]
        p_win = max(player_score, key=player_score.get) # 
        best_score = max(player_score.values())
        # if there is more than one person with the winning hand, check for highest card
        # if sum(value == player_score[p_win] for value in player_score.values()) > 1:
        if list(player_score.values()).count(best_score) > 1:
            
            #winner_score = max(player_score.values())
            kickers_to_check = score_to_kicker[best_score]
            #list of players also with that hand
            winners = [p for p in player_score.keys() if player_score[p]==p_score]

            ### reworking
            same_hand = False
            same_handed = []
            #calculate the highest card that makes each winning hand a winner
            for winner in winners:
                self.assign_winning_hand(winner, p_score)
                # cards = winner.get_hand() + self.community_cards
                # if p_score == 1:
                #     winner.win_combo = max(cards).rank
                #     winner.winning_hand = winner.win_combo
                # elif p_score == 2:
                #     winner.win_combo = max(Game.get_x_of_a_kind(cards, 2))
                #     winner.winning_hand = winner.win_combo
                # elif p_score == 3:
                #     pairs = Game.get_two_pair(cards)
                #     pairs.sort()
                #     pairs.reverse()
                #     new_pairs =[pairs[0], pairs[1]]
                #     winner.win_combo = new_pairs
                #     winner.winning_hand = winner.win_combo
                # elif p_score == 4:
                #     winner.win_combo = max(Game.get_x_of_a_kind(cards, 3))
                #     winner.winning_hand = winner.win_combo
                # elif p_score == 5:
                #     winner.win_combo = max(Game.get_straight(cards))
                #     winner.winning_hand = winner.win_combo
                # elif p_score == 6:
                #     winner.win_combo = max(Game.get_flush(cards))
                #     winner.winning_hand = winner.win_combo
                # elif p_score == 7:
                #     #like two pair, return list. when comparing
                #     winner.win_combo = Game.get_full_house(cards)
                #     winner.winning_hand = winner.win_combo
                # elif p_score == 8:
                #     #foak
                #     winner.win_combo = max(Game.get_x_of_a_kind(cards, 4))
                #     winner.winning_hand = winner.win_combo
                # elif p_score == 9:
                #     winner.win_combo = max(Game.get_straight(cards))
                #     winner.winning_hand = winner.win_combo
                # else:
                #     raise ValueError('Invalid p_score')

            largest_combo = max(winners, key=attrgetter('win_combo')).win_combo
            for w in winners:
                if w.win_combo == largest_combo:
                    same_handed.append(w)
            if len(same_handed) > 1 and kickers_to_check != 0:
                #check kickers
                check_kickers = []
                highest = False
                player_win_combo = {}
                current_kickers = set()
                cards_checked = set()
                kickers_checked = 0
                
                if kickers_to_check == 0:
                    raise ValueError('shouldnt be here')
                while not highest:
                    current_kickers = set()
                    player_win_combo = {}
                    for p in same_handed:
                        #remove the 'winning' (same) combo 
                        
                        # only with two pair does a win combination contain two cards
                        # In this case, they will be equal
                        check_ranks = self.cards_to_ranks(self.community_cards + p.get_hand())
                        check_kickers = []
                        
                        
                        for r in check_ranks:
                            if r not in cards_checked:
                                if isinstance(p.win_combo, list):
                                    #if the win combo is a 2 pair list
                                    if r not in p.win_combo:
                                        check_kickers.append(r)
                                    else:
                                        cards_checked.add(r)
                                elif r != p.win_combo:
                                    check_kickers.append(r)
                                else:
                                    cards_checked.add(r)
                        
                        if len(check_kickers) != 0:
                            #no more kickers to check
                            
                            p.win_combo = max(check_kickers)
                            player_win_combo[p] = max(check_kickers)
                            current_kickers.add(max(check_kickers))
                        else:
                            draw = True
                            p_win = same_handed
                            return p_win, best_score
                    if len(current_kickers) == 0:
                        raise ValueError('No kickers left to check, should have been caught in previous if statement.')
                    if sum(value == max(current_kickers) for value in player_win_combo.values()) == 1:    
                        highest = True
                        p_win = max(player_win_combo, key=player_win_combo.get)
                        return [p_win], best_score
                    next_handed = []
                    for p in same_handed:
                        if p.win_combo == max(current_kickers):
                            next_handed.append(p)
                            cards_checked.add(p.win_combo)
                    if len(next_handed)==0:
                        raise ValueError('No players left to check kickers from...')
                    same_handed = next_handed
                    
                    kickers_checked +=1
                    if kickers_checked == kickers_to_check:
                        #if we've exhausted the number of possible kickers (highest five cards)
                        return same_handed, best_score
                if p_win == None:
                    raise TypeError('Shits FUcked')
                return p_win, best_score
                
            else:
                winner = same_handed
                if winner == None:
                    raise TypeError('Shits FUcked')
                else:
                    return winner, best_score
        
        else:
            
            if [p_win] == None:
                raise ValueError('P_win cannot be empty')
            winner = p_win
            p_score = player_score[p_win]
            self.assign_winning_hand(winner, p_score)
            # assign winning hand
            # cards = winner.get_hand() + self.community_cards
            # if p_score == 1:
            #     winner.win_combo = max(cards).rank
            #     winner.winning_hand = winner.win_combo
            # elif p_score == 2:
            #     winner.win_combo = max(Game.get_x_of_a_kind(cards, 2))
            #     winner.winning_hand = winner.win_combo
            # elif p_score == 3:
            #     pairs = Game.get_two_pair(cards)
            #     pairs.sort()
            #     pairs.reverse()
            #     new_pairs =[pairs[0], pairs[1]]
            #     winner.win_combo = new_pairs
            #     winner.winning_hand = winner.win_combo
            # elif p_score == 4:
            #     winner.win_combo = max(Game.get_x_of_a_kind(cards, 3))
            #     winner.winning_hand = winner.win_combo
            # elif p_score == 5:
            #     winner.win_combo = max(Game.get_straight(cards))
            #     winner.winning_hand = winner.win_combo
            # elif p_score == 6:
            #     winner.win_combo = max(Game.get_flush(cards))
            #     winner.winning_hand = winner.win_combo
            # elif p_score == 7:
            #     #like two pair, return list. when comparing
            #     winner.win_combo = Game.get_full_house(cards)
            #     winner.winning_hand = winner.win_combo
            # elif p_score == 8:
            #     #foak
            #     winner.win_combo = max(Game.get_x_of_a_kind(cards, 4))
            #     winner.winning_hand = winner.win_combo
            # elif p_score == 9:
            #     winner.win_combo = max(Game.get_straight(cards))
            #     winner.winning_hand = winner.win_combo
            # elif p_score == 10:
            #     winner.win_combo = max(Game.get_straight(cards))
            #     winner.winning_hand = winner.win_combo
            # else:
            #     raise ValueError('Invalid p_score')
            return [p_win], p_score

    # GETTERS

    def get_player_history(self, p_name):
        players_chip_history = []
        player = [p for p in self.players if p.name == p_name][0]

        players_chip_history = [h[player] for h in self.chip_history]
        return players_chip_history

    def get_winner(self):
            return self.winner

    def get_hand_count(self):
        '''
        Returns the hand count
        '''
        return self.hand_count + 1

    def get_chip_counts(self):
        chips = []
        for p in self.original_players:
           chips.append(p.stack)
        return chips 
    
    def get_player_chip_count(self, p_number):
        return self.original_players[p_number].stack

    def get_player_fitnesses(self):
        '''Using winning a hand for +5 fitness, losing a hand for -0.5 fitness and going out for -10 fitness.'''
        fits = []
        for p in self.original_players:
            fits.append(p.fitness)
        return fits

    def get_all_player_chips(self):
        player_chips = {}
        for i,p in enumerate(self.original_players):
            player_chips[i] = p.stack
        
        return player_chips

    # SETTERS

    def update_out_of_tournament_players(self):
        '''
        Reset the 'out_players' list
        '''
        new_players = []
        for p in self.players:
            if not p.out_of_tournament:
                new_players.append(p)
            elif p.out_of_tournament and p not in self.out_players:
                self.out_players.append(p)
        self.players = new_players

    # UTILITY FUNCTIONS

    def update_chip_matrix(self, player):
        i = self.original_players.index(player)
        for l in range(6):
            p = self.original_players[l]
            if i != l:
                self.win_loss_matrix[i][l] += self.hand_chip_counts[p]
                self.win_loss_matrix[l][i] -= self.hand_chip_counts[p]

    def assign_winning_hand(self, winner, score):
        '''
        Takes a player and their score and assigns them their winning combination
        '''
        cards = winner.get_hand() + self.community_cards
        if score == 1:
            winner.win_combo = max(cards).rank
            winner.winning_hand = winner.win_combo
        elif score == 2:
            winner.win_combo = max(Game.get_x_of_a_kind(cards, 2))
            winner.winning_hand = winner.win_combo
        elif score == 3:
            pairs = Game.get_two_pair(cards)
            pairs.sort()
            pairs.reverse()
            new_pairs =[pairs[0], pairs[1]]
            winner.win_combo = new_pairs
            winner.winning_hand = winner.win_combo
        elif score == 4:
            winner.win_combo = max(Game.get_x_of_a_kind(cards, 3))
            winner.winning_hand = winner.win_combo
        elif score == 5:
            winner.win_combo = max(Game.get_straight(cards))
            winner.winning_hand = winner.win_combo
        elif score == 6:
            winner.win_combo = max(Game.get_flush(cards))
            winner.winning_hand = winner.win_combo
        elif score == 7:
            #like two pair, return list. when comparing
            winner.win_combo = Game.get_full_house(cards)
            winner.winning_hand = winner.win_combo
        elif score == 8:
            #foak
            winner.win_combo = max(Game.get_x_of_a_kind(cards, 4))
            winner.winning_hand = winner.win_combo
        elif score == 9:
            winner.win_combo = max(Game.get_straight(cards))
            winner.winning_hand = winner.win_combo
        elif score == 10:
            winner.win_combo = max(Game.get_straight(cards))
            winner.winning_hand = winner.win_combo
        else:
            raise ValueError('Invalid p_score')

    def populate_player_pool(self, players, newround=False):
        '''
        Function that, for each part of the action, will repopulate the player 'pool' (cycle) for the correct order with
        whoever is in the hand.
        
        Params:
        newround (default=False): declares whether the round is starting anew
        '''
        players_in_hand = []
        for p in self.players:
            p.on_table = 0
            if not p.out_of_tournament and not p.out:
                players_in_hand.append(p)
        else:
            return players_in_hand

    def reset_out_players(self):
        for p in self.players:
            if p.stack != 0:
                p.out = False

    def is_tournament_over(self):
        '''
        Returns true if every player's stack is equal to zero (bar one).
        '''
        out=0
        for p in self.players:
            if p.stack == 0:
                out+=1
        if out == len(self.players) - 1:
            self.winner = [w for w in self.players if w.stack != 0][0]
            return True
        else:
            return False
        
    def hand_won(self, player):
        if self.pprint: print('%s wins the hand' % player.position)
        if player.evolve: player.fitness += 1
        player.add_to_stack(self.pot)

    def check_bigger_winner(self, players):
        for p in players:
            pass

    def assign_bot_strategy(self, strategy, playerNo):
        for p in self.original_players:
            if p.bot and self.original_players.index(p) == playerNo:
                p.assignStrategy(strategy)

    def assign_network_weights(self, preweights,postweights, playerNo):
        for p in self.original_players:
            if p.bot and self.original_players.index(p) == playerNo:
                p.setPreflopWeights(preweights)
                p.setPostflopWeights(postweights)

    def assign_rand_strat(self):
        for p in self.original_players:
            p.assignStrategy([randint(0,100), randint(0,100),randint(0,100),randint(0,10),randint(0,10),randint(0,100),randint(0,10),randint(0,10),randint(0,100),randint(0,10),randint(0,10),randint(0,100)])

    def cards_to_ranks(self, cards):
        return [c.rank for c in cards]

    def check_same_cards(self, players, number_of_kickers, cards_left):
        player_and_kicker = {}
        for p in players:
            player_and_kicker[p] = p.win_combo
        largest_kicker = max(player_and_kicker.values())
        if sum(value == largest_kicker for value in player_and_kicker.values()) > 1 and number_of_kickers > 0:
                # check_cards = self.community_cards + p.get_hand()
                # check_ranks = []
                # for c in check_cards:
                #     check_ranks.append(c.rank)
                others_cards = []
                for p in players:
                    others_cards.append(p.hand.first.rank)
                    others_cards.append(p.hand.second.rank)
                for p in players:
                    remove_win = []
                    #remove win should be only the players cards + community - win combo
                    #remove_win = [r for r in cards_left if r != p.win_combo and r != largest_kicker]
                    for r in cards_left:
                        if r in others_cards and (r == p.hand.first.rank or r == p.hand.second.rank):
                            remove_win.append(r)
                        elif r in others_cards and r != p.hand.first.rank:
                            pass
                        elif r in others_cards and r != p.hand.first.rank:
                            pass
                        elif r not in others_cards and r != p.win_combo and r != largest_kicker:
                            remove_win.append(r)
                    if remove_win == []:
                        draw = True
                    else:
                        draw = False
                        p.win_combo = max(remove_win)
                if not draw:
                    return self.check_same_cards(players, number_of_kickers-1, remove_win)
        else:
            if number_of_kickers == 0:
                return players
            else:
                if max(player_and_kicker, key=player_and_kicker.get) == None:
                    raise TypeError('shits fucked')
                return [max(player_and_kicker, key=player_and_kicker.get)]
    
    # STATIC METHODS (not object dependent)

    @staticmethod
    def is_royal_flush(cards):
        '''
        cards: seven cards composed of community and hole cards
        '''
        rf_cards = 0
        suits = [0,0,0,0]
        if Game.is_flush(cards):
            flush = Game.get_flush(cards)
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
    @staticmethod
    def is_x_of_a_kind(cards, x):
        count = 0
        ranks = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == x:
                return True
        return False
    @staticmethod
    def get_x_of_a_kind(cards, x):
        count = 0
        ranks = []
        pairs = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == x:
                pairs.append(r)
        return pairs
    @staticmethod
    def is_straight(cards):
        count = 0
        ranks = []
        straight = False
        check_ace = False
        for c in cards:
            ranks.append(c.rank)
        ranks.sort()
        ranks = set(ranks)
        ranks = list(ranks)
        ranks.sort()

        for i in range(len(ranks)-1):
            if Rank.difference(ranks[i], ranks[i+1]) == 1:
                count+=1
                if count == 4:
                    straight = True
                    break
                if count == 3:
                    check_ace = True
            else:
                count = 0
        if straight:
            return True
        elif check_ace and len(ranks) >= 5:
            if ranks[0] == Rank('2') and ranks[1] == Rank('3') and ranks[2] == Rank('4') and ranks[3] == Rank('5') and Rank('A') in ranks:
                #need a way to check if there is an A2345 straight
                return True
        else:
            return False
    @staticmethod
    def get_straight(cards):
        ranks = []
        straight = []
        count = 0
        check_ace = False
        for c in cards:
            ranks.append(c.rank)
        ranks.sort()
        for i in range(len(ranks)-1):


            if Rank.difference(ranks[i], ranks[i+1]) == 1:
                
                if ranks[i] not in straight:
                    straight.append(ranks[i])
                straight.append(ranks[i+1])
                count += 1
            elif count == 3:
                check_ace = True
            else:
                count = 0
        if check_ace and len(ranks) >= 5:
            if ranks[0] == Rank('2') and ranks[1] == Rank('3') and ranks[2] == Rank('4') and ranks[3] == Rank('5') and Rank('A') in ranks:
                straight.append(Rank('A'))
                straight.sort()

        return straight
    @staticmethod    
    def is_flush(cards):
        suits = Game.count_suits(cards)
        if suits[0] >= 5 or suits[1] >= 5 or suits[2] >= 5 or suits[3] >= 5:
            return True
        else:
            return False
    @staticmethod
    def count_suits(cards):
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
    @staticmethod
    def get_flush(cards):
        if Game.is_flush(cards):
            suits = Game.count_suits(cards)
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
    @staticmethod
    def conv_suits(cards):
        suits = [c.suit for c in cards]
        return suits
    @staticmethod
    def is_straight_flush(cards):
        if Game.is_flush(cards) and Game.is_straight(cards):
            flush = Game.get_flush(cards)
            flush_ranks = [f.rank for f in flush]
            straight_ranks = Game.get_straight(cards)
            if len(set(flush_ranks) & set(straight_ranks)) >= 5:
                return True
            else:
                return False
        else:
            return False
    @staticmethod
    def is_two_pair(cards):
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
    @staticmethod
    def get_two_pair(cards):
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
    @staticmethod
    def is_full_house(cards):
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
    @staticmethod
    def get_full_house(cards):
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
    @staticmethod
    def get_highest_combo(cards):
        '''
        takes seven cards and returns a number corresponding to the poker hand ranking ()
        '''
        ranking = 0
        if Game.is_royal_flush(cards):
            
            ranking = 10
        elif Game.is_straight_flush(cards):
            ranking = 9
        elif Game.is_x_of_a_kind(cards, 4):
            ranking = 8
        elif Game.is_full_house(cards):
            ranking = 7
        elif Game.is_flush(cards):
            ranking = 6
        elif Game.is_straight(cards):
            ranking = 5
        elif Game.is_x_of_a_kind(cards, 3):
            ranking = 4
        elif Game.is_two_pair(cards):
            ranking = 3
        elif Game.is_x_of_a_kind(cards, 2):
            ranking = 2
        else:
            # high card
            ranking = 1
        return ranking


class Player(object):

    def __init__(self, name):
        self.name = name
        self.stack = 0
        self.hand = None
        self.position = None
        self.out = False
        self.on_table = 0
        self.win_combo = None
        self.winning_hand = None
        self.out_of_tournament = False
        self.all_in = False
        self.action_numbers = {'fold':1,'call':2,'check':3,'bet':4,'raise':5}
        self.bot = False
        self.manual = False
    def position(self, p):
        self.position = p

    def deal(self, c1, c2):
        #Combos can be compared
        self.hand = Combo.from_cards(c1, c2)

    def get_action_type(self):
        '''
        cbet: the amount the player wishes to bet
        returns: an integer between 1 and 5 which corresponds to action (fold,call,check,bet,raise) 
        '''
        return int(input('enter type: '))

    def get_action_amount(self, action, min_bet, current_bet):
        return int(input('enter amount: '))

    def add_to_pot(self, amount):
        if int(amount) > self.stack:
            amount = self.stack
            self.stack = 0
        else:
            self.stack -= amount
        #if self.pprint: print('adding %i to pot' % amount)
        self.on_table += amount

    def add_to_stack(self, amount):
        self.stack += amount

    def get_hand(self):
        c1, c2 = self.hand.first, self.hand.second
        return [c1, c2]

class ManualPlayer(Player):

    def __init__(self, name):
        super().__init__(name)
        #self.action_numbers = {'fold':1,'call':2,'check':3,'bet':4,'raise':5}
    
    def getActionType(self):
        action = input('Action: ')
        amount = input('Amount: ')
        return self.action_numbers[action], amount

class RandomPlayer(Player):

    def __init__(self, name):
        super().__init__(name)
        self.evolve = False

    def getActionType(self, p_round, action_left, pleft, out, community_cards, pot, cbet):
        action_type = randint(1, 5)
        if cbet > 0:
            action_type = randint(1, 3)
            if action_type == 1:
                return 1, 0
            if action_type == 2:
                return 2, 0
            if action_type == 3:
                if cbet > self.stack:
                    return 2, 0
                else:
                    return 5, 4
        elif cbet == 0:
            if action_type == 2:
                return 3, 0
            elif action_type == 5 or action_type == 4:
                return 4, 2
            else:
                return action_type, 0
        elif action_type == 1:
            return 2, 0
        else:
            return action_type, 0

    def get_action_amount(self, action, min_bet, current_bet):
        if action == 4:
            #bet must be min bet or higher
            amount = randint(min_bet, min_bet *2)
            if amount > self.stack:
                amount = self.stack
            return amount
        elif action == 5:
            #raise must be current bet*2 or higher
            amount = randint(current_bet*2, current_bet*3)
            if amount > self.stack:
                amount = self.stack
            return amount
        else:
            return 0

class RangePlayer(Player):

    def __init__(self, name):
        super().__init__(name)
        #Here we define a range for the player
        self.hand_range = list(Range("A8o+ KTo+ QJo+ KTs+ JT+ A2s+ 22+ T9 98 87s 76s T9o 98o").combos)
        
    def get_action_type(self, cbet, preflop):
        '''
        cbet = current bet
        '''
        if preflop:
            #preflop we will bet our hands in range 3x the big blind
            if self.hand in self.hand_range:
                if cbet > 0:
                    raise_chance = 70
                    call_chance = 20
                    bet_chance = 0
                else:
                    bet_chance =90
                    raise_chance=0
                    call_chance = 0
                fold_chance = 10
                check_chance = 0
            else:
                fold_chance = 100
                call_chance = 0
                raise_chance = 0
                bet_chance = 0
                check_chance = 0
        
        
        else:
            #TODO: now want to see if we have made hands
            if cbet > 0:
                raise_chance = 20
                call_chance = 40
                fold_chance = 40
                check_chance = 0
                bet_chance = 0
            else:
                check_chance = 60
                bet_chance = 35
                fold_chance = 5
                call_chance = 0
                raise_chance = 0
        r = uniform(0,1)
        action_types = ['fold'] * fold_chance + ['call'] * call_chance + ['check'] * check_chance + ['bet'] * bet_chance + ['raise'] * raise_chance
        action = choice(action_types)
        return self.action_numbers[action]

    def get_action_amount(self, action, min_bet, current_bet):
        if action == 4:
            #bet must be min bet or higher
            amount = randint(min_bet, min_bet *2)
            if amount > self.stack:
                amount = self.stack
            return amount
        elif action == 5:
            #raise must be current bet*2 or higher
            amount = randint(current_bet*2, current_bet*3)
            if amount > self.stack:
                amount = self.stack
            return amount
        else:
            return 0

class EvolvePlayer(Player):

    # We define the default preflop range as all combos, sorted from worst to best. 
    def __init__(self, name):
        super().__init__(name)
        self.strategy = []
        self.bot = True

    def assignStrategy(self, strategy):
        '''
        Takes as input a 4x3 2d Array [[a,b,c]
                                       [d,e,f]   
                                       [g,h,i]
                                       [j,k,l]]
        Where each row corresponds to 
        a,d,g,j: matrices of bits representing the cards the player would want to stay in the hand. Corresponds to a 'top x percent' of all poker hands 
        For a, this means top percent of all possible starting hands
        For d,g, and j, this means the top percent of winnings hands (e.g. 1 to 10 where 1 is high card, and 10 is straight flush)
        b,e,h,k:  integers representing the cards the player would regard as strong. Corresponds to a 'top x percent' of all poker hands
        c,f,i,l: integers representing the amount the player would ideally like to bet, from bb*2 to the stack size
        '''
        ## Function needed to return top hands for each stage
        ## PreFlop can be precalculated (e.g. AA,AK,KK,AQ,AJ...)

        #Assign preflop
        self.strategy = strategy
        preflop_cont = self.strategy[0]
        self.preflop_cont = BASE_HAND_RANGE[round(-(len(BASE_HAND_RANGE) * (preflop_cont/100))):]
        preflop_best = self.strategy[1]
        self.preflop_best = BASE_HAND_RANGE[round(-(len(BASE_HAND_RANGE) * (preflop_best/100))):]
        self.preflop_bet = self.strategy[2]

        # Assign flop strategy
        self.flop_cont = self.strategy[3]
        self.flop_best = self.strategy[4]
        self.flop_bet = self.strategy[5]

        # Assign turn strategy
        self.turn_cont = self.strategy[6]
        self.turn_best = self.strategy[7]
        self.turn_bet = self.strategy[8]

        # Assign river strategy
        self.river_cont = self.strategy[9]
        self.river_best = self.strategy[10]
        self.river_bet = self.strategy[11]

    def get_action_type_and_amount(self, cbet, round, community_cards):
        if round == 0:
            best = self.preflop_best
            cont = self.preflop_cont
            bet = self.preflop_bet
        elif round == 1:
            best = self.flop_best
            cont = self.flop_cont
            bet = self.flop_bet
        elif round == 2:
            best = self.flop_best
            cont = self.flop_cont
            bet = self.flop_bet
        elif round == 3:
            best = self.flop_best
            cont = self.flop_cont
            bet = self.flop_bet
        else:
            raise ValueError('invalid round number')

        if round == 0:
            # PREFLOP
            #print(self.hand)
            if self.hand in best:
                
                # the hand is among what is considered best, so raise

                #if the amount they want to raise to is less than or equal to double the current raise, just call
                if bet <= cbet*2:
                    return 2, 0
                else:
                    return 5, self.min_stack_bet(bet)
            elif self.hand in cont:
                # the hand warrants staying in, so call
                return 2, 0
            else:
                # the hand is not what we consider playable, so fold
                return 1, 0
        else:
            if Game.get_highest_combo(([self.hand.first,self.hand.second] + community_cards)) >= cont:
                # Our current made hand is at least as good as what we would want to continue
                if cbet == 0:
                    #check
                    return 3, 0
                else:
                    #call
                    return 2,0
            elif Game.get_highest_combo([self.hand.first,self.hand.second] + community_cards) >= best:
                # The hand is among what we would consider the strongest, so raise/bet
                if cbet == 0:
                    return 4, self.min_stack_bet(bet) # bet if no current bet
                else:
                    if bet <= cbet*2: #if the current bet is equal to or more than we would like to bet/raise it up to then we should just call
                        return 2, 0
                    else:
                        return 5, self.min_stack_bet(bet) # raise if current bet
            else:
                return 1,0
        
    def min_stack_bet(self, bet):
        return min(bet, self.stack)

class NeuralPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.preflop_network = PokerNetwork(8, 5, 3)
        self.postflop_network = PokerNetwork(7, 5, 3)
        self.bot, self.evolve = True, True
        self.fitness = 0
    def setPreflopWeights(self, preflop_weights):
        self.preflop_network.setWeightsLinear(preflop_weights)
    def setPostflopWeights(self, postflop_weights):
        self.postflop_network.setWeightsLinear(postflop_weights)

    def getActionType(self, preflop, to_act_after, acted, out, community_cards, potsize, cbet):
        if preflop == 0:
            preflop = True
        else:
            preflop = False
        if preflop:
            inputs = [int(CheckAce(self.hand.first)), int(CheckAce(self.hand.second)), int(JackOrBetter(self.hand.first)), int(JackOrBetter(self.hand.second)), ConvToRange(to_act_after),ConvToRange(acted), ConvToRange(out), ConvToRange(potsize)]
            output = self.preflop_network.feedForward(inputs)
        else:
            cards = self.get_hand() + community_cards
            inputs = [int(MadeHand(cards)), int(AtLeastTwoPair(cards)), int(AtLeastFlush(cards)), ConvToRange(to_act_after), ConvToRange(acted),ConvToRange(out), ConvToRange(potsize)]
            output = self.postflop_network.feedForward(inputs)
        decision = np.argmax(output, axis=0)
        #bet = output[3] * potsize
        #print(decision)
        if decision == 0:
            return (1, 0)
        elif decision == 1:
            if cbet > 0:
                return (2,0) #call
            else:
                return (3,0) #check
        elif decision == 2:
            if cbet == 0:
                return (4,2) #bet
            else:
                return (5,4) #raise

class PokerNetwork:
    def __init__(self, numInput, numHidden1, numOutput):
        self.fitness = 0
        self.numInput = numInput + 1 # Add bias node from input to hidden layer 1 only
        self.numHidden1 = numHidden1 # Feel free to adapt the code to add more biases if you wish
        #self.numHidden2 = numHidden2
        self.numOutput = numOutput

        self.w_i_h1 = np.random.randn(self.numHidden1, self.numInput) 
        #self.w_h1_h2 = np.random.randn(self.numHidden2, self.numHidden1) 
        self.w_h1_o = np.random.randn(self.numOutput, self.numHidden1)

        self.ReLU = lambda x : max(0,x)

    def softmax(self, x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()
    
    def feedForward(self, inputs):
        inputsBias = inputs[:]
        inputsBias.insert(len(inputs),1)             # Add bias input

        h1 = np.dot(self.w_i_h1, inputsBias)         # feed input to hidden layer 1
        h1 = [self.ReLU(x) for x in h1]              # Activate hidden layer1
        
        # h2 = np.dot(self.w_h1_h2, h1)                 # feed layer 1 to hidden layer 2
        # h2 = [self.ReLU(x) for x in h2]              # Activate hidden layer 2

        output = np.dot(self.w_h1_o, h1)             # feed to output layer
        #output = [self.sigmoid(x) for x in output]   # Activate output layer
        return self.softmax(output)

    def getWeightsLinear(self):
        flat_w_i_h1 = list(self.w_i_h1.flatten())
        #flat_w_h1_h2 = list(self.w_h1_h2.flatten())
        flat_w_h1_o = list(self.w_h1_o.flatten())
        return( flat_w_i_h1 + flat_w_h1_o )

    def setWeightsLinear(self, Wgenome):
        numWeights_I_H1 = self.numHidden1 * self.numInput
        #numWeights_H1_H2 = self.numHidden2 * self.numHidden1
        numWeights_H1_O = self.numOutput * self.numHidden1

        self.w_i_h1 = np.array(Wgenome[:numWeights_I_H1])
        self.w_i_h1 = self.w_i_h1.reshape((self.numHidden1, self.numInput))
        
        # self.w_h1_h2 = np.array(Wgenome[numWeights_I_H1:(numWeights_H1_H2+numWeights_I_H1)])
        # self.w_h1_h2 = self.w_h1_h2.reshape((self.numHidden2, self.numHidden1))

        self.w_h1_o = np.array(Wgenome[numWeights_I_H1:])
        self.w_h1_o = self.w_h1_o.reshape((self.numOutput, self.numHidden1))

class TAGPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.bot, self.evolve, self.harcoded = True, False, True

    def getActionType(self, preflop, to_act_after, acted, out, community_cards, potsize, cbet):
        # A TAG (tight-aggrssive) player should fold most of their hands that are below a small range (20%?)
        # and continue with good holdings. They may sometimes bluff. They rarely 'limp' into a pot
        # i.e., call on the preflop
        bet_size = 2
        raise_size = 4
        bluffChance = 0.07
        limpChance = 0.1

        openRange = randint(10, 20) #oppen with between 10 and 20 percent of hands
        pfOpenWith = BASE_HAND_RANGE[round(-(len(BASE_HAND_RANGE) * (openRange/100))):]
        
        flopContinue = randint(1, 3)  #This represents the player continuing with a hand of strength 0-3 or better. E.g.
                                      # a flopContinue value of "1" means the player continues with a pair or better
        riverContinue = randint(2, 4)
        turnContinue = randint(2, 5)



        # The higher the hand strength this, the more chance they will raise
        # e.g. a strength of 1 means they will raise 10% of the time

        
        
        if preflop > 0:
            hand_strength = Game.get_highest_combo(([self.hand.first,self.hand.second] + community_cards))
            continueBetRaiseChance = (hand_strength ** 1.2)/10 # This makes it so the chance of betting or raising
                                                          # with a good hand is exponential based on strength
        else:
            hand_strength = None
        
        
        if preflop == 0:
            if self.hand in pfOpenWith:
                # want to open, so raise
                return 5, raise_size
            #hand is not good enough to open, so either bluff or limp
            elif uniform(0, 1) < limpChance:
                return 2, 0 #call
            elif uniform(0, 1) < bluffChance:
                return 5, raise_size # bluff a 3-bet
            else:
                return 1, 0 # fp;d
        elif preflop == 1:
            #flop
            # Use the % chance of continuing on the flop. 
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= flopContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0 #no bet so always check if hand is bad
        elif preflop == 2:
            #river
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= riverContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0
        elif preflop == 3:
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= turnContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0
        if betorRaise:
            if cbet == 0:
                return 4, bet_size
            else:
                return 5, raise_size

class LAGPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.bot, self.evolve, self.harcoded = True, False, True

    def getActionType(self, preflop, to_act_after, acted, out, community_cards, potsize, cbet):
        # A TAG (tight-aggrssive) player should fold most of their hands that are below a small range (20%?)
        # and continue with good holdings. They may sometimes bluff. They rarely 'limp' into a pot
        # i.e., call on the preflop
        bet_size = 2
        raise_size = 4
        bluffChance = 0.12 # LAGs bluff and limp a lot more
        limpChance = 0.4

        openRange = randint(30, 40) # LAGs open with a lot more hands
        pfOpenWith = BASE_HAND_RANGE[round(-(len(BASE_HAND_RANGE) * (openRange/100))):]
        
        flopContinue = randint(0, 2)  #This represents the player continuing with a hand of strength 0-3 or better. E.g.
                                      # a flopContinue value of "1" means the player continues with a pair or better
        riverContinue = randint(1, 3)
        turnContinue = randint(2, 4)



        # The higher the hand strength this, the more chance they will raise
        # e.g. a strength of 1 means they will raise 10% of the time

        
        
        if preflop > 0:
            hand_strength = Game.get_highest_combo(([self.hand.first,self.hand.second] + community_cards))
            continueBetRaiseChance = (hand_strength ** 1.2)/10 # This makes it so the chance of betting or raising
                                                          # with a good hand is exponential based on strength
        else:
            hand_strength = None
        
        
        if preflop == 0:
            if self.hand in pfOpenWith:
                # want to open, so raise
                return 5, raise_size
            #hand is not good enough to open, so either bluff or limp
            elif uniform(0, 1) < limpChance:
                return 2, 0 #call
            elif uniform(0, 1) < bluffChance:
                return 5, raise_size # bluff a 3-bet
            else:
                return 1, 0 # fp;d
        elif preflop == 1:
            #flop
            # Use the % chance of continuing on the flop. 
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= flopContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0 #no bet so always check if hand is bad
        elif preflop == 2:
            #river
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= riverContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0
        elif preflop == 3:
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= turnContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0
        if betorRaise:
            if cbet == 0:
                return 4, bet_size
            else:
                return 5, raise_size

class LPPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.bot, self.evolve, self.harcoded = True, False, True

    def getActionType(self, preflop, to_act_after, acted, out, community_cards, potsize, cbet):
        # A loose-passive player (or calling station) will often just call hands down
        # and very rarely bluff
        bet_size = 2
        raise_size = 4
        bluffChance = 0.03 # LAGs bluff and limp a lot more
        limpChance = 0.65

        openRange = randint(30, 50) # LAGs open with a lot more hands
        pfOpenWith = BASE_HAND_RANGE[round(-(len(BASE_HAND_RANGE) * (openRange/100))):]
        
        flopContinue = randint(0, 2)  #This represents the player continuing with a hand of strength 0-3 or better. E.g.
                                      # a flopContinue value of "1" means the player continues with a pair or better
        riverContinue = randint(1, 3)
        turnContinue = randint(2, 4)



        # The higher the hand strength this, the more chance they will raise
        # e.g. a strength of 1 means they will raise 10% of the time

        
        
        if preflop > 0:
            hand_strength = Game.get_highest_combo(([self.hand.first,self.hand.second] + community_cards))
            continueBetRaiseChance = (hand_strength**1.4)/100 # This makes it so the chance of betting or raising
                                                      # with a good hand is exponential based on strength
        else:
            hand_strength = None
        
        
        if preflop == 0:
            if self.hand in pfOpenWith:
                # want to open, so raise
                return 5, raise_size
            #hand is not good enough to open, so either bluff or limp
            elif uniform(0, 1) < limpChance:
                return 2, 0 #call
            elif uniform(0, 1) < bluffChance:
                return 5, raise_size # bluff a 3-bet
            else:
                return 1, 0 # fp;d
        elif preflop == 1:
            #flop
            # Use the % chance of continuing on the flop. 
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= flopContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0 #no bet so always check if hand is bad
        elif preflop == 2:
            #river
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= riverContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0
        elif preflop == 3:
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= turnContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0
        if betorRaise:
            if cbet == 0:
                return 4, bet_size
            else:
                return 5, raise_size

class TPPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.bot, self.evolve, self.harcoded = True, False, True

    def getActionType(self, preflop, to_act_after, acted, out, community_cards, potsize, cbet):
        # A tight-passive player (or a nit) will rarely get involved in hands,
        # and when they do just call
        bet_size = 2
        raise_size = 4
        bluffChance = 0.02 # LAGs bluff and limp a lot more
        limpChance = 0.1

        openRange = randint(5, 20) # LAGs open with a lot more hands
        pfOpenWith = BASE_HAND_RANGE[round(-(len(BASE_HAND_RANGE) * (openRange/100))):]
        
        flopContinue = randint(0, 3)  #This represents the player continuing with a hand of strength 0-3 or better. E.g.
                                      # a flopContinue value of "1" means the player continues with a pair or better
        riverContinue = randint(2, 4)
        turnContinue = randint(2, 5)



        # The higher the hand strength this, the more chance they will raise
        # e.g. a strength of 1 means they will raise 10% of the time

        
        
        if preflop > 0:
            hand_strength = Game.get_highest_combo(([self.hand.first,self.hand.second] + community_cards))
            continueBetRaiseChance = (hand_strength**1)/10 # This makes it so the chance of betting or raising
                                                             # with a good hand is exponential based on strength
        else:
            hand_strength = None
        
        
        if preflop == 0:
            if self.hand in pfOpenWith:
                # want to open, so raise
                return 5, raise_size
            #hand is not good enough to open, so either bluff or limp
            elif uniform(0, 1) < limpChance:
                return 2, 0 #call
            elif uniform(0, 1) < bluffChance:
                return 5, raise_size # bluff a 3-bet
            else:
                return 1, 0 # fp;d
        elif preflop == 1:
            #flop
            # Use the % chance of continuing on the flop. 
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= flopContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0 #no bet so always check if hand is bad
        elif preflop == 2:
            #river
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= riverContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0
        elif preflop == 3:
            if uniform(0, 1) < continueBetRaiseChance:
                betorRaise = True
            elif uniform(0, 1) < bluffChance:
                betorRaise= True
            elif hand_strength >= turnContinue:
                if cbet > 0:
                    return 2, 0 # just call
                else:
                    return 3, 0
            else:
                if cbet > 0:
                    
                    if uniform(0, 1) < bluffChance:
                        return 2,0
                    else:
                        return 1,0
                else:
                    return 3, 0
        if betorRaise:
            if cbet == 0:
                return 4, bet_size
            else:
                return 5, raise_size

def CheckAce(card):
    return card.rank == Rank('A') or card.rank == Rank('A')

def JackOrBetter(card):
    return card.rank >= Rank('J') or card.rank >= Rank('J')

def ConvToRange(number):
    return 1 / 1 + abs(number)

def MadeHand(cards):
    return Game.get_highest_combo(cards) > 0

def AtLeastTwoPair(cards):
    return Game.get_highest_combo(cards) > 2
        
def AtLeastFlush(cards):
    return Game.get_highest_combo(cards) > 5
