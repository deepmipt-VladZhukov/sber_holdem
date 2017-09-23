SUIT_MAP = {
    0: 'C',
    1: 'D',
    2: 'H',
    3: 'S'
}

RANK_MAP = {
    0: '2',
    1: '3',
    2: '4',
    3: '5',
    4: '6',
    5: '7',
    6: '8',
    7: '9',
    8: 'T',
    9: 'J',
    10: 'Q',
    11: 'K',
    12: 'A'
}

SUIT_MAP_INV = {v: k for k, v in SUIT_MAP.items()}
SUITS = [v for k, v in sorted(SUIT_MAP.items(), key=lambda x: x[0])]

RANK_MAP_INV = {v: k for k, v in RANK_MAP.items()}
RANKS = [v for k, v in sorted(RANK_MAP.items(), key=lambda x: x[0])]


i = 0
DECK = {}
DECK_INV = {}
for s in SUITS:
    for r in RANKS:
        DECK[s+r] = i
        DECK_INV[i] = s + r
        i += 1


def cards2ints(cards):
    return [(RANK_MAP_INV[c[1]], SUIT_MAP_INV[c[0]]) for c in cards]
