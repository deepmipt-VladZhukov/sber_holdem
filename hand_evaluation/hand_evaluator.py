from card import DECK, DECK_INV, cards2ints
from random import randint
from combinations import combinationF7
from itertools import chain


class Deck(object):
    def __init__(self):
        self.deck = DECK.copy()

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
