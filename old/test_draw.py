from poker import Card, Rank, Suit
from sixhanded import Player

community_cards = [Card('9h'), Card('Ah'),Card('5h'), Card('2c'),Card('6c')]


def showdown(players):
    player_score = {}
    for p in players:
        hole_and_community = p.get_hand() + community_cards
        player_score[p] = get_highest_combo(hole_and_community)
    p_win = max(player_score, key=player_score.get)
    p_score = player_score[max(player_score, key=player_score.get)]
    # if there is more than one person with the winning hand, check for highest card
    if sum(value == p_score for value in player_score.values()) > 1:
        #list of players also with that hand
        winners = [p for p in player_score.keys() if player_score[p]==p_score]
        
        #high card
        if p_score == 1:
            current_highest = p_win
            draw = False
            drawers = []
            for winner in winners:
                winner.win_combo = max(winner.get_hand() + community_cards)
                if winner != current_highest:
                    if current_highest.win_combo < winner.win_combo:
                        draw = False
                        current_highest = winner
                    elif current_highest.win_combo == winner.win_combo:
                        draw = True
                        drawers.append(winner)
            if draw:
                return 'draw', p_score
            else:
                return current_highest.name, p_score
                
        #pair
        elif p_score == 2:
            current_highest = p_win
            draw = False
            drawers = []
            for winner in winners:
                winner.win_combo = max(get_x_of_a_kind(winner.get_hand() + community_cards, 2))
                if winner != current_highest:
                    if current_highest.win_combo < winner.win_combo:
                        draw = False
                        current_highest = winner
                    elif current_highest.win_combo == winner.win_combo:
                        draw = True
                        drawers.append(winner)
            if draw:
                return 'draw', p_score
            else:
                return current_highest.name, p_score

        #two pair over two pair
        elif p_score == 3:
            pass

        #toak over toak
        elif p_score == 4:
            pass
        #straight over straight
        elif p_score == 5:
            pass
        #flush over flush
        elif p_score == 6:
            current_highest = p_win
            draw = False
            drawers = []
            for winner in winners:
                winner.win_combo = max(get_flush(winner.get_hand() + community_cards))
                if winner != current_highest:
                    if current_highest.win_combo < winner.win_combo:
                        draw = False
                        current_highest = winner
                    elif current_highest.win_combo == winner.win_combo:
                        draw = True
                        drawers.append(winner)
            if draw:
                return 'draw', p_score
            else:
                return current_highest.name, p_score

        #fh over fh
        elif p_score == 7:
            pass
        #foak over foak
        elif p_score == 8:
            pass
        #sf over sf
        elif p_score == 9:
            pass
        else:
            raise ValueError('Something has gone very wrong')
        

    else:
        return p_win.name, p_score

def is_royal_flush(cards):
    '''
    cards: seven cards composed of community and hole cards
    '''
    rf_cards = 0
    suits = [0,0,0,0]
    if is_flush(cards):
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

def is_x_of_a_kind(cards, x):
    count = 0
    ranks = []
    for c in cards:
        ranks.append(c.rank)
    for r in ranks:
        if ranks.count(r) == x:
            return True
    return False

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

def is_straight(cards):
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

def is_flush(cards):
    suits = count_suits(cards)
    if suits[0] >= 5 or suits[1] >= 5 or suits[2] >= 5 or suits[3] >= 5:
        return True
    else:
        return False

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

def get_flush(cards):
    if is_flush(cards):
        suits = count_suits(cards)
        for i in range(5, 7):
            if i in suits:
                suit = suits.index(i)
        if suit == 0:
            suit = Suit('h')
        elif suit == 1:
            suit = Suit('d')
        elif suit == 2:
            suit = Suit('s')
        else:
            suit = 'c'
        l = [c for c in cards if c.suit == suit]
        l.sort()
        return l
    else:
        raise ValueError('error: not a flush, code broken')

def conv_suits(cards):
    suits = [c.suit for c in cards]
    return suits

def conv_rankings(cards):
    pass

def is_straight_flush(cards):
    if is_flush(cards) and is_straight(cards):
        return True
    else:
        return False

def get_two_of_a_kind(cards):
    #want the highest toak here
    ranks = []
    number_of_toak = 0
    for c in cards:
        ranks.append(c.rank)
    for r in ranks:
        if ranks.count(r) == 2:
            number_of_toak += 1
            card_return = []
            for c in cards:
                if c.rank == r:
                    card_return.append(c)
            return card_return
    raise ValueError('error')

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

    # raise ValueError('error')
    # if is_x_of_a_kind(cards, 2):

    #     cards_left = [x for x in cards if x not in get_two_of_a_kind(cards)]
    #     if is_x_of_a_kind(cards_left, 2):
    #         return True
    # else:
    #     return False

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

def get_highest_combo(cards):
    '''
    takes seven cards and returns a number corresponding to the poker hand ranking ()
    '''
    if is_royal_flush(cards):
        return 10
    elif is_straight_flush(cards):
        return 9
    elif is_x_of_a_kind(cards, 4):
        return 8
    elif is_full_house(cards):
        return 7
    elif is_flush(cards):
        return 6
    elif is_straight(cards):
        return 5
    elif is_x_of_a_kind(cards, 3):
        return 4
    elif is_two_pair(cards):
        return 3
    elif is_x_of_a_kind(cards, 2):
        return 2
    else:
        # high card
        return 1

p1 = Player('p1')
p2 = Player('p2')
p3 = Player('p3')

p1.deal(Card('Kc'), Card('Kd'))
p2.deal(Card('9d'), Card('As'))
p3.deal(Card('As'), Card('Qc'))

print(is_flush(p1.get_hand() + community_cards))

print(is_flush(p2.get_hand() + community_cards))

winner, score = showdown([p1, p2])
print(winner, score)