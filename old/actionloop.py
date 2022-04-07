import random 
def action_loop(self, preflop=False):
    if preflop:
        current_bet = self.bb
    else:
        current_bet = 0

    action_left = len(self.players_in_hand)
    out = 6 - action_left
    while action_left != 0:
        player_to_act = next(self.player_pool)
        print('%s to act...' % player_to_act.position)
        
        action_type = to_act.get_action_type()
        amount = get_action_amount(action_type)

        if action_type == 1:
            #fold
            player_to_act.out = True
            action_left -=1
            out+=1
            print('Fold.')
        elif action_type == 2:
            #call
            action_left -= 1
            player_to_act.add_to_pot(current_bet)
            print('Call. Pot = %i' % self.pot)
        elif action_type == 3:
            #check
            action_left -= 1
            print('Check.')
        elif action_type == 4:
            #bet
            action_left = len(self.players_in_hand) - out
            player_to_act.add_to_pot(amount)
            current_bet = amount
            print('Bet, size %i' % (amount))
        elif action_type == 5:
            #raise
            action_left = len(self.players_in_hand) - out
            player_to_act.add_to_pot(amount)
            current_bet = amount
            print('Raise, size %i' % (amount))
        else:
            raise ValueError('invalid action')

    
def get_action_type(self):
    action_type = random.randint(1, 5)
    return action_type

def get_action_amount(self, action, min_bet, current_bet):
    if action == 4:
        #bet must be min bet or higher
        return random.randint(min_bet, min_bet *2)
    elif action == 5:
        #raise must be current bet*2 or higher
        return random.randint(current_bet*2, current_bet*3)
    else:
        return 0

# out_of_tournament = 0
# action_left = len(self.players_in_hand)
# out = 6 - action_left
# while action_left != 0:
#     to_act = next(self.player_pool)
#     if not to_act.out:
#         print('%s to act...' % to_act.position)
#         while action[0] == 0:
#             action = to_act.get_action(current_bet, self.bb)
#         if action[0] == 1:
#             #folded
#             to_act.out = True
#             action_left -= 1
#             out+=1
#         elif action[0] == 2:
#             #call
#             adding_to_pot = current_bet - to_act.in_pot
#             self.pot += to_act.add_to_pot(adding_to_pot)
#             print('Call. Pot = %i' % self.pot)
#             action_left -= 1
#         elif action[0] == 3:
#             #check
#             action_left -= 1
#             print('Check')
#         elif action[0] == 4:
#             #bet. don't need to worry about 'in_pot' because you can only bet when there's no current bet
#             self.pot += to_act.add_to_pot(action[1])
#             current_bet = action[1]
#             print('Bet of %i. Pot = %i' % (action[1], self.pot))
#             action_left = 5 - out
#         elif action[0] == 5:
#             #raise
#             adding_to_pot = action[1] - to_act.in_pot
#             self.pot += to_act.add_to_pot(adding_to_pot)
#             current_bet = adding_to_pot
#             print('Raise of %i. Pot = %i' % (action[1], self.pot))
#             action_left = 5- out
#         action = (0,0)
#     # else:
#     #     out+=1
#     #     action_left -= 1
#     if out == 5:
#         #check if all players are out of chips
#         for player in self.players:
#             if player.stack == 0:
#                 out_of_tournament += 1
#         if out_of_tournament == 5:
#             winner = [p for p in self.player_pool if player.out == False]
#             self.tournament_over = True
#             print('Tournament over, winner is %s!' % winner)
#         else:
#             break
# #end of round
# return out