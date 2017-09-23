import numpy as np


def combinationF5(a, cr1, cs1, cr2, cs2, cr3, cs3, cr4, cs4, cr5, cs5):
    f = 0
    sf = 0
    if cs1 == cs2 and cs2 == cs3 and cs3 == cs4 and cs4 == cs5:
        f = 1
    Rank = a[cr1][cr2][cr3][cr4][cr5]
    if f == 1:
        return 50000000 + Rank
    return Rank


def combinationF7(a, cr1, cs1, cr2, cs2, cr3, cs3, cr4, cs4, cr5, cs5, cr6, cs6, cr7, cs7):
    Comb = np.zeros(21)
    Comb[0] = combinationF5(a, cr1, cs1, cr2, cs2, cr3, cs3, cr4, cs4, cr5, cs5)
    Comb[1] = combinationF5(a,cr1, cs1, cr2, cs2, cr3, cs3, cr4, cs4, cr6, cs6)
    Comb[2] = combinationF5(a,cr1, cs1, cr2, cs2, cr3, cs3, cr5, cs5, cr6, cs6)
    Comb[3] = combinationF5(a,cr1, cs1, cr2, cs2, cr4, cs4, cr5, cs5, cr6, cs6)
    Comb[4] = combinationF5(a,cr1, cs1, cr3, cs3, cr4, cs4, cr5, cs5, cr6, cs6)
    Comb[5] = combinationF5(a,cr2, cs2, cr3, cs3, cr4, cs4, cr5, cs5, cr6, cs6)

    Comb[6] = combinationF5(a,cr1, cs1, cr2, cs2, cr3, cs3, cr4, cs4, cr7, cs7)
    Comb[7] = combinationF5(a,cr1, cs1, cr2, cs2, cr3, cs3, cr5, cs5, cr7, cs7)
    Comb[8] = combinationF5(a,cr1, cs1, cr2, cs2, cr4, cs4, cr5, cs5, cr7, cs7)
    Comb[9] = combinationF5(a,cr1, cs1, cr3, cs3, cr4, cs4, cr5, cs5, cr7, cs7)
    Comb[10] =combinationF5(a,cr2, cs2, cr3, cs3, cr4, cs4, cr5, cs5, cr7, cs7)

    Comb[11] = combinationF5(a,cr1, cs1, cr2, cs2, cr3, cs3, cr6, cs6, cr7, cs7)
    Comb[12] = combinationF5(a,cr1, cs1, cr2, cs2, cr4, cs4, cr6, cs6, cr7, cs7)
    Comb[13] = combinationF5(a,cr1, cs1, cr3, cs3, cr4, cs4, cr6, cs6, cr7, cs7)
    Comb[14] = combinationF5(a,cr2, cs2, cr3, cs3, cr4, cs4, cr6, cs6, cr7, cs7)

    Comb[15] = combinationF5(a,cr1, cs1, cr2, cs2, cr5, cs5, cr6, cs6, cr7, cs7)
    Comb[16] = combinationF5(a,cr1, cs1, cr3, cs3, cr5, cs5, cr6, cs6, cr7, cs7)
    Comb[17] = combinationF5(a,cr2, cs2, cr3, cs3, cr5, cs5, cr6, cs6, cr7, cs7)

    Comb[18] = combinationF5(a,cr1, cs1, cr4, cs4, cr5, cs5, cr6, cs6, cr7, cs7)
    Comb[19] = combinationF5(a,cr2, cs2, cr4, cs4, cr5, cs5, cr6, cs6, cr7, cs7)

    Comb[20] = combinationF5(a,cr3, cs3, cr4, cs4, cr5, cs5, cr6, cs6, cr7, cs7)
    max = 0;

    if (Comb[0] > max):
         max = Comb[0];
    if (Comb[1] > max):
         max = Comb[1];
    if (Comb[2] > max):
         max = Comb[2];
    if (Comb[3] > max):
         max = Comb[3];
    if (Comb[4] > max):
         max = Comb[4];
    if (Comb[5] > max):
         max = Comb[5];
    if (Comb[6] > max):
         max = Comb[6];
    if (Comb[7] > max):
         max = Comb[7];
    if (Comb[8] > max):
         max = Comb[8];
    if (Comb[9] > max):
         max = Comb[9];
    if (Comb[10] > max):
         max = Comb[10]
    if (Comb[11] > max):
         max = Comb[11]
    if (Comb[12] > max):
         max = Comb[12]
    if (Comb[13] > max):
         max = Comb[13]
    if (Comb[14] > max):
         max = Comb[14]
    if (Comb[15] > max):
         max = Comb[15]
    if (Comb[16] > max):
         max = Comb[16]
    if (Comb[17] > max):
         max = Comb[17]
    if (Comb[18] > max):
         max = Comb[18]
    if (Comb[19] > max):
         max = Comb[19]
    if (Comb[20] > max):
         max = Comb[20]

    return max
