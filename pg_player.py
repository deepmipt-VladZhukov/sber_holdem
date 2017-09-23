from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.card import Card
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np

NB_SIMULATION = 500

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
        # self.conv3 = nn.Conv1d(8, 16, 4, stride=1)

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


class PgPlayer(BasePokerPlayer):

    def __init__(self):
        self.FOLD = 0
        self.CALL = 1
        self.MIN_RAISE = 2
        self.MAX_RAISE = 3
        self.PRINT = True
        self.start_stack = 0

    def __init__(self):
        self.policy = Policy()
        self.policy.load_state_dict(torch.load('bot3.pth'))

    def select_action(self, state, desk):
        state = torch.from_numpy(state).float().unsqueeze(0)
        desk = torch.from_numpy(desk).float().unsqueeze(0)
        probs = self.policy(Variable(state), Variable(desk))
        action = probs.multinomial()
        self.policy.saved_actions.append(action)
        return action.data

    def declare_action(self, valid_actions, hole_card, round_state):
        current_players = 0
        stack = 0
        for i in round_state['seats']:
            if self.uuid == i['uuid']:
                stack = i['stack']
            if i['state'] == 'participating':
                current_players += 1
        if current_players < 2:
            current_players = 2

        community_card = round_state['community_card']
        m = np.zeros((4,13))
        for i in range(len(community_card)):
            card = HandyCard.from_str(community_card[i])
            m[card.suit][card.rank-2] = 1
        for i in range(len(hole_card)):
            card = HandyCard.from_str(hole_card[i])
            m[card.suit][card.rank-2] = 1
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=NB_SIMULATION,
            nb_player=current_players,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        bank = round_state['pot']['main']['amount']
        big_blind_amount = 2*round_state['small_blind_amount']

        if valid_actions[2]['amount']['min'] > 0:
            raise_amount = valid_actions[2]['amount']['min'] /big_blind_amount
        else:
            raise_amount = valid_actions[1]['amount']/big_blind_amount

        action = self.select_action(np.log((np.array([stack/big_blind_amount, bank/big_blind_amount,
         valid_actions[1]['amount']/big_blind_amount, raise_amount, win_rate/current_players])+0.00001)), m)[0, 0]

        if self.FOLD == action:
            if self.PRINT:
                print("{} fold".format(round_state['street']), self.actions_in_game)
            return valid_actions[0]['action'], valid_actions[0]['amount']
        elif self.CALL == action:
            if self.PRINT:
                print("{} call {}".format(round_state['street'], valid_actions[1]['amount']))
            return valid_actions[1]['action'], valid_actions[1]['amount']
        elif self.MIN_RAISE == action:
            if self.PRINT:
                print("{} raise {}".format(round_state['street'], valid_actions[2]['amount']['min']))
            return valid_actions[2]['action'], valid_actions[2]['amount']['min']
        elif self.MAX_RAISE == action:
            if self.PRINT:
                print("{} allin {}".format(round_state['street'], valid_actions[2]['amount']['max']))
            return valid_actions[2]['action'], valid_actions[2]['amount']['max']
        else:
            raise Exception("Invalid action [ %s ] is set" % action)

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']
        stack = 0
        for i in game_info['seats']:
            if self.uuid == i['uuid']:
                stack = i['stack']
        self.start_stack = stack

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

