try:
    from card import DECK, DECK_INV, cards2ints, SUIT_MAP
    from combinations import combinationF7
except:
    from hand_evaluation.card import DECK, DECK_INV, cards2ints, SUIT_MAP
    from hand_evaluation.combinations import combinationF7
from random import randint
from itertools import chain
import json
import os
dir_path = os.path.dirname(os.path.abspath(__file__))


class Deck(object):
    def __init__(self):
        self.deck = DECK.copy()
        with open(os.path.join(dir_path, '../stats.json'), 'r') as f:
            self.top_combo = json.load(f)

    def clear(self):
        self.deck = DECK.copy()

    def take_card(self, card):
        self.deck.pop(card, None)

    def add_card(self, card):
        i = DECK[card]
        self.deck[card] = i

    def sample_card(self):
        while True:
            i = randint(0, 51)
            c = DECK_INV[i]
            if c in self.deck:
                self.take_card(c)
                return c

    def sample_two_cards(self, top_range=169):
        cnt = 0
        while True:
            cnt += 1
            if cnt > top_range:
                return [self.deck.sample_card() for _ in range(2)]
            pair_id = randint(0, top_range - 1)
            pair_str = self.top_combo[pair_id][0]
            if len(pair_str)==3:
                col1 = randint(0, 3)
                col2 = col1
            else:
                cols = [0, 1, 2, 3]
                col1 = randint(0, 3)
                cols.remove(col1)
                col2 = cols[randint(0, 2)]
            suit1 = SUIT_MAP[col1]
            suit2 = SUIT_MAP[col2]
            cart1 = suit1 + pair_str[0]
            cart2 = suit2 + pair_str[1]
            if cart1 in self.deck and cart2 in self.deck:
                self.take_card(cart1)
                self.take_card(cart2)
                return [cart1, cart2]

    def __len__(self):
        return len(self.deck)


def win_rate(num_sim, arr, my_cards, comm_cards):
    dec = Deck()

    # take cards form deck
    for c in my_cards + comm_cards:
        dec.take_card(c)

    n_comm_cards = len(comm_cards)
    point_win = 0
    for _ in range(num_sim):

        while len(comm_cards) < 5:
            comm_cards.append(dec.sample_card())

        opp_cards = [dec.sample_card() for _ in range(2)]

        opp_ints = cards2ints(opp_cards)
        comm_ints = cards2ints(comm_cards)
        my_ints = cards2ints(my_cards)

        my_val = combinationF7(arr,
            *list(chain.from_iterable(comm_ints + my_ints))
        )
        opp_val = combinationF7(arr,
            *list(chain.from_iterable(comm_ints + opp_ints)))

        # add back sampled cards
        for c in opp_cards + comm_cards[n_comm_cards:]:
            dec.add_card(c)
        comm_cards = comm_cards[:n_comm_cards]

        if my_val > opp_val:
            point_win += 1
        elif my_val == opp_val:
            point_win += 0.5

    return point_win / num_sim

def win_rate2(num_sim, arr, my_cards, comm_cards, top_range=169, number_of_opp_players=8):
    dec = Deck()

    # take cards form deck
    for c in my_cards + comm_cards:
        dec.take_card(c)

    n_comm_cards = len(comm_cards)
    point_win = 0
    for _ in range(num_sim):

        while len(comm_cards) < 5:
            comm_cards.append(dec.sample_card())
        comm_ints = cards2ints(comm_cards)
        my_ints = cards2ints(my_cards)
        my_val = combinationF7(arr,
            *list(chain.from_iterable(comm_ints + my_ints))
        )
        all_opp_cards = []
        all_opp_val = []
        for i in range(number_of_opp_players):
            opp_cards = dec.sample_two_cards(top_range=top_range)
            for c in opp_cards:
                # dec.add_card(c)
                all_opp_cards.append(c)
            opp_ints = cards2ints(opp_cards)
            opp_val = combinationF7(arr,
                *list(chain.from_iterable(comm_ints + opp_ints)))
            all_opp_val.append(opp_val)
        # add back sampled cards
        opp_val = max(all_opp_val)
        for c in comm_cards[n_comm_cards:] + all_opp_cards:
            dec.add_card(c)
        comm_cards = comm_cards[:n_comm_cards]

        if my_val > opp_val:
            point_win += 1
        elif my_val == opp_val:
            point_win += 0.5

    return point_win / num_sim
