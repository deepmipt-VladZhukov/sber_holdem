import numpy as np
import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.engine.card import Card
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from torch.autograd import Variable

from simple_players.aggressive_player import AggressivePlayer
from simple_players.caller_player import CallerPlayer
from simple_players.honest_player import HonestPlayer
from simple_players.random_player import RandomPlayer
from pg.pg_player import PgPlayer as current_PgPlayer

gamma = 0.95
NB_SIMULATION = 1000
PRINT = True


class HandyCard(Card):

  SUIT_MAP = {
    0  : 'C',
    1  : 'D',
    2  : 'H',
    3 : 'S'
  }

  def __init__(self, suit, rank):
    self.suit = suit
    self.rank = 14 if rank == 1 else rank

class Policy(nn.Module):
    def __init__(self):
        super(Policy, self).__init__()
        self.affine1 = nn.Linear(5, 16)
        self.affine2 = nn.Linear(16, 32)
        self.affine3 = nn.Linear(56, 4)
        self.conv1 = nn.Conv1d(4, 4, 8, stride=1)
        self.conv2 = nn.Conv1d(4, 8, 4, stride=1)

        self.saved_actions = []
        self.rewards = []

    def forward(self, x, desk):
        x = F.elu(self.affine1(x))
        state_out = F.elu(self.affine2(x))

        desk_out = F.elu(self.conv1(desk))
        desk_out = F.elu(self.conv2(desk_out))
        # desk_out = F.elu(self.conv3(desk_out))
        desk_out = desk_out.view(-1, 24)
        out = F.softmax(F.elu(self.affine3(torch.cat([state_out, desk_out],1))))
        return out


policy = Policy()
optimizer = optim.Adam(policy.parameters(), lr=1e-4)
policy.load_state_dict(torch.load('pg/state/bot3.pth'))

def select_action(state, desk):
    state = torch.from_numpy(state).float().unsqueeze(0)
    desk = torch.from_numpy(desk).float().unsqueeze(0)
    probs = policy(Variable(state), Variable(desk))
    action = probs.multinomial()
    policy.saved_actions.append(action)
    return action.data

def finish_episode():
    R = 0
    rewards = []
    for r in policy.rewards[::-1]:
        if r != 0:
            R = r
        else :
            R = r + gamma * R
        rewards.insert(0, R)

    if np.count_nonzero(rewards) >0:
        # print(rewards)
        rewards = torch.Tensor(rewards)
        for action, r in zip(policy.saved_actions, rewards):
            action.reinforce(r)
        optimizer.zero_grad()
        autograd.backward(policy.saved_actions, [None for _ in policy.saved_actions])
        optimizer.step()
    del policy.rewards[:]
    del policy.saved_actions[:]

epsilon = 1

class PgPlayer(BasePokerPlayer):

    def __init__(self):
        self.FOLD = 0
        self.CALL = 1
        self.MIN_RAISE = 2
        self.MAX_RAISE = 3
        self.start_stack = 0
        self.global_stack = 0
        self.random_action = 0
        self.real_action = 0
        self.big_blind_amount = 1

    def declare_action(self, valid_actions, hole_card, round_state):
        global policy, epsilon
        community_card = round_state['community_card']
        m = np.zeros((4,13))
        for i in range(len(community_card)):
            card = HandyCard.from_str(community_card[i])
            m[card.suit][card.rank-2] = 1
        for i in range(len(hole_card)):
            card = HandyCard.from_str(hole_card[i])
            m[card.suit][card.rank-2] = 1

        current_players = 0
        stack = 0
        for i in round_state['seats']:
            if self.uuid == i['uuid']:
                stack = i['stack']
            if i['state'] == 'participating':
                current_players += 1
        if current_players < 2:
            current_players = 2

        if  round_state['street'] == 'preflop':
            win_rate = estimate_hole_card_win_rate(
                nb_simulation=500,
                nb_player=current_players,
                hole_card=gen_cards(hole_card),
                community_card=gen_cards(community_card)
            )
        else :
            win_rate = estimate_hole_card_win_rate(
                nb_simulation=NB_SIMULATION,
                nb_player=current_players,
                hole_card=gen_cards(hole_card),
                community_card=gen_cards(community_card)
            )

        bank = round_state['pot']['main']['amount']
        self.big_blind_amount = 2*round_state['small_blind_amount']

        if valid_actions[2]['amount']['min'] > 0:
            raise_amount =  valid_actions[2]['amount']['min'] /self.big_blind_amount
        else :
            raise_amount = valid_actions[1]['amount']/self.big_blind_amount

        action = select_action(np.log((np.array([stack/self.big_blind_amount, bank/self.big_blind_amount,
         valid_actions[1]['amount']/self.big_blind_amount, raise_amount, win_rate/current_players])+0.00001)), m)[0, 0]

        if np.random.random() < epsilon:
            action = np.random.randint(4)
            self.random_action+=1
        else :
            self.real_action += 1

        policy.rewards.append(0)
        if self.FOLD == action:
            if PRINT:
                print("{} fold".format(round_state['street']))
            return valid_actions[0]['action'], valid_actions[0]['amount']
        elif self.CALL == action:
            if PRINT:
                print("{} call {}".format(round_state['street'], valid_actions[1]['amount']))
            return valid_actions[1]['action'], valid_actions[1]['amount']
        elif self.MIN_RAISE == action:

            if valid_actions[2]['amount']['min'] == -1:
                if PRINT:
                    print("{} call {}".format(round_state['street'],  valid_actions[1]['amount']))
                return valid_actions[1]['action'], valid_actions[1]['amount']

            if PRINT:
                print("{} raise {}".format(round_state['street'], valid_actions[2]['amount']['min']))

            return valid_actions[2]['action'], valid_actions[2]['amount']['min']
        elif self.MAX_RAISE == action and win_rate > 0.85 and (round_state['street'] == 'turn' or round_state['street'] == 'river'):

            if valid_actions[2]['amount']['max'] == -1:
                if PRINT:
                    print("{} call {}".format(round_state['street'],  valid_actions[1]['amount']))
                return valid_actions[1]['action'], valid_actions[1]['amount']

            if PRINT:
                print("{} allin {}".format(round_state['street'], valid_actions[2]['amount']['max']))

            return valid_actions[2]['action'], valid_actions[2]['amount']['max']
        elif action == self.MAX_RAISE:

            if valid_actions[2]['amount']['min'] == -1:
                if PRINT:
                    print("{} call {}".format(round_state['street'],  valid_actions[1]['amount']))
                return valid_actions[1]['action'], valid_actions[1]['amount']

            if PRINT:
                print("{} 2 min raise {}".format(round_state['street'], 2*valid_actions[2]['amount']['min']))

            return valid_actions[2]['action'], 2 * valid_actions[2]['amount']['min']
        else:
            if PRINT:
                print("{} fold".format(round_state['street']))
            return valid_actions[0]['action'], valid_actions[0]['amount']

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']
        stack = 0
        for i in game_info['seats']:
            if self.uuid == i['uuid']:
                stack = i['stack']
        self.global_stack = stack
        self.start_stack = stack


    def receive_round_start_message(self, round_count, hole_card, seats):
        # if self.global_stack > 0:
        #     print("_"*50)
        #     print(hole_card)
        pass

    def receive_street_start_message(self, street, round_state):
        # if len(round_state['community_card']) > 0 and self.global_stack > 0:
        #     print(round_state['community_card'])
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        stack = 0
        for i in round_state['seats']:
            if self.uuid == i['uuid']:
                stack = i['stack']
        if len(policy.rewards) > 0:
            if stack == 0:
                policy.rewards[-1] = (3*(stack - self.global_stack))/self.big_blind_amount
            else:
                policy.rewards[-1] = (stack - self.global_stack)/self.big_blind_amount

        self.global_stack = stack
        finish_episode()


my_player = PgPlayer()

config = setup_config(max_round=50, initial_stack=1500, small_blind_amount=15)
config.register_player(name="p1", algorithm=my_player)
config.register_player(name="p2", algorithm=HonestPlayer())
config.register_player(name="p3", algorithm=HonestPlayer())
config.register_player(name="p4", algorithm=current_PgPlayer())
config.register_player(name="p5", algorithm=current_PgPlayer())
# config.register_player(name="p5", algorithm=RandomPlayer())
# config.register_player(name="p6", algorithm=RandomPlayer())
# config.register_player(name="p7", algorithm=CallerPlayer())
# config.register_player(name="p8", algorithm=CallerPlayer())


for i_episode in range(1000000):
    # state = env.reset()
    game_result = start_poker(config, verbose=0)
    print(game_result['players'][0])
    print("random {} real {}".format(my_player.random_action, my_player.real_action))
    my_player.random_action = 0
    my_player.real_action = 0
    if epsilon > 0:
        epsilon -= 0.05
    torch.save(policy.state_dict(), 'pg/state/bot3.pth')

