from random import shuffle
from poker import Card, Rank, Suit, card, Combo

from old.sixhandedtournament_attempt1 import Player

win_percents = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0}
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

def conv_suits(cards):
    suits = [c.suit for c in cards]
    return suits

def conv_rankings(cards):
    pass

def is_straight_flush(cards):
    if is_flush(cards) and is_straight(cards):
        flush = get_flush(cards)
        flush_ranks = [f.rank for f in flush]
        straight_ranks = get_straight(cards)
        if len(set(flush_ranks) & set(straight_ranks)) >= 5:
            return True
        else:
            return False
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
    if check_ace:
        if ranks[0] == Rank('2') and ranks[1] == Rank('3') and ranks[2] == Rank('4') and ranks[3] == Rank('5') and ranks[6] == Rank('A'):
            straight.append(Rank('A'))
            straight.sort()

    return straight

def is_straight_flush(cards):
    if is_flush(cards) and is_straight(cards):
        flush = get_flush(cards)
        flush_ranks = [f.rank for f in flush]
        straight_ranks = get_straight(cards)
        if len(set(flush_ranks) & set(straight_ranks)) >= 5:
            return True
        else:
            return False
    else:
        return False

def get_highest_combo(cards):
        '''
        takes seven cards and returns a number corresponding to the poker hand ranking ()
        '''
        ranking = 0
        if is_royal_flush(cards):
            
            ranking = 10
        elif is_straight_flush(cards):
            ranking = 9
        elif is_x_of_a_kind(cards, 4):
            ranking = 8
        elif is_full_house(cards):
            ranking = 7
        elif is_flush(cards):
            ranking = 6
        elif is_straight(cards):
            ranking = 5
        elif is_x_of_a_kind(cards, 3):
            ranking = 4
        elif is_two_pair(cards):
            ranking = 3
        elif is_x_of_a_kind(cards, 2):
            ranking = 2
        else:
            # high card
            ranking = 1
        win_percents[ranking] += 1
        return ranking

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
def cards_to_ranks(cards):
    return [c.rank for c in cards]

def test_same_handed(ktc, community_cards, same_handed, winner_score, player_score):
    highest = False
    player_win_combo = {}
    current_kickers = set()
    cards_checked = set()
    kickers_checked = 0
    kickers_to_check = ktc
    check_kickers = []


    if kickers_to_check == 0:
        raise ValueError('shouldnt be here')
    while not highest:
        current_kickers = set()
        player_win_combo = {}
        for p in same_handed:
            #remove the 'winning' (same) combo 
            
            # only with two pair does a win combination contain two cards
            # In this case, they will be equal
            check_ranks = cards_to_ranks(community_cards + p.get_hand())
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
                return p_win, winner_score
        if len(current_kickers) == 0:
            print('OOPS')
        if sum(value == max(current_kickers) for value in player_win_combo.values()) == 1:    
            highest = True
            p_win = max(player_win_combo, key=player_win_combo.get)
            return [p_win], winner_score
        next_handed = []
        for p in same_handed:
            if p.win_combo == max(current_kickers):
                next_handed.append(p)
                cards_checked.add(p.win_combo)
        if len(next_handed)==0:
            print('hm')
        same_handed = next_handed
        
        kickers_checked +=1
        if kickers_checked == kickers_to_check:
            #if we've exhausted the number of possible kickers (highest five cards)
            return same_handed, winner_score

#c1 = [Card('4c'), Card('Jh'), Card('Kh'), Card('Th'), Card('Jc'), Card('Ah'), Card('Qh')]
# c2 = [Card('Ah'), Card('Ac'), Card('Ah'), Card('Ah'), Card('Kc'), Card('Kh'), Card('Qh')]
# c3 = [Card('Jc'), Card('Tc'), Card('Tc'), Card('Kc'), Card('Ts'), Card('Ad'), Card('Qh')]
# c4 = [Card('2c'), Card('3c'), Card('4c'), Card('5c'), Card('6s'), Card('Kc'), Card('Ks')]
# fh_test = [Card('2c'), Card('4c'), Card('2s'), Card('3h'), Card('2h'), Card('5c'), Card('3d')]
# print(is_royal_flush(c1))
# #print(is_x_of_a_kind(c2, 4))
# print(is_straight(c3))
# # print(is_two_pair(c4))
# # print(is_full_house(fh_test))
# #print(get_flush(c1))
# print(is_straight_flush(c4))

# deck = list(Card)
# random_seven = [deck.pop() for __ in range(7)]

# _iter = 10000

# for i in range(_iter):
#     if i % 10000 == 0:
#         print(i)
#     deck = list(Card)
#     shuffle(deck)
#     random_seven = [deck.pop() for __ in range(7)]
#     get_highest_combo(random_seven)
# w =list(win_percents.values())
# print([x / _iter * 100 for x in w])



p1 = Player('Player 1')
p2 =Player('Player 2')
p3 = Player('Player 3')
players = [p1,p2,p3]
p1.hand = Combo('Td4c')
p2.hand = Combo('AdTc')
p3.hand = Combo('Qd2s')
community_cards = [Card('7♥'), Card('5♥'), Card('7♦'), Card('5♦'), Card('2♣')]

pairs = get_two_pair(community_cards + p1.get_hand())
pairs.sort()
pairs.reverse()
new_pairs =[pairs[0], pairs[1]]
p1.win_combo = new_pairs

pairs = get_two_pair(community_cards + p2.get_hand())
pairs.sort()
pairs.reverse()
new_pairs =[pairs[0], pairs[1]]
p2.win_combo = new_pairs

pairs = get_two_pair(community_cards + p3.get_hand())
pairs.sort()
pairs.reverse()
new_pairs =[pairs[0], pairs[1]]
p3.win_combo = new_pairs

player_score = {p1:3,p2:3,p3:3}
winner, score = test_same_handed(1, community_cards, players, 3, player_score)

print(winner[0].name, score)