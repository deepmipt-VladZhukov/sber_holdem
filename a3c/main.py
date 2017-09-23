from __future__ import print_function

import argparse
import os
import sys
from a3c.model import ActorCritic
import torch
import torch.optim as optim
import torch.multiprocessing as mp
import torch.nn as nn
import torch.nn.functional as F
from a3c.shared_adam import SharedAdam
from aggressive_player import AggressivePlayer
from honest_player import HonestPlayer
from pypokerengine.api.game import setup_config, start_poker
from a3c.player import A3Cplayer
from random_player import RandomPlayer
from caller_player import CallerPlayer
import numpy as np
torch.manual_seed(123)

def train(rank, shared_model, optimizer):
    my_player = A3Cplayer(rank, shared_model, optimizer)

    config = setup_config(max_round=50, initial_stack=1500, small_blind_amount=15)
    config.register_player(name="p1", algorithm=my_player)
    config.register_player(name="p2", algorithm=HonestPlayer())
    config.register_player(name="p3", algorithm=AggressivePlayer())
    config.register_player(name="p4", algorithm=RandomPlayer())
    config.register_player(name="p5", algorithm=CallerPlayer())

    for i_episode in range(1000000):
        game_result = start_poker(config, verbose=0)
        if my_player.epsilon > 0:
            my_player.epsilon -= 0.05


def test(rank, shared_model):
    torch.manual_seed(123)
    my_player = A3Cplayer(rank, shared_model, training=False)
    my_player.epsilon = 0

    config = setup_config(max_round=50, initial_stack=1500, small_blind_amount=15)
    config.register_player(name="p1", algorithm=my_player)
    config.register_player(name="p2", algorithm=HonestPlayer())
    config.register_player(name="p3", algorithm=AggressivePlayer())
    config.register_player(name="p4", algorithm=RandomPlayer())
    config.register_player(name="p5", algorithm=CallerPlayer())

    for i_episode in range(1000000):
        game_result = start_poker(config, verbose=0)
        print(rank, game_result['players'][0], "random {} real {}".format(my_player.random_action, my_player.real_action))
        my_player.random_action = 0
        my_player.real_action = 0


if __name__ == '__main__':

    torch.manual_seed(123)

    shared_model = ActorCritic()
    shared_model.share_memory()
    optimizer = SharedAdam(shared_model.parameters(), lr=0.001)
    optimizer.share_memory()

    processes = []
    p = mp.Process(target=test, args=(8, shared_model))

    p.start()
    processes.append(p)
    for rank in range(1):
        p = mp.Process(target=train, args=(rank, shared_model, optimizer))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
