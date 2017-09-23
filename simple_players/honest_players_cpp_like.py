import pickle
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import os
dir_path = os.path.abspath(__file__)


def load_arr():
    fnama_arr = os.path.join(dir_path, '../hand_evaluation/Array.pkl')
    with open(fnama_arr, 'rb') as f:
        arr = pickle.load(f)
    return arr


class HonestPlayer(BasePokerPlayer):
    def __init__(self, nb_sim=100, thr=0.6):
        self.nb_sim = nb_sim
        self.thr = thr

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=self.nb_sim,
            nb_player=2,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )
        if win_rate > self.thr:
            action = valid_actions[2]
            return action['action'], action['amount']['max']
        else:
            action = valid_actions[0]  # fetch FOLD action info
        return action['action'], action['amount']

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


class HonestPlayer2(BasePokerPlayer):
    def __init__(self, np_simulations=3000, thr1=0.7, thr2=0.65, thr3=0.6):
        self.np_simulations = np_simulations
        self.arr = load_arr()
        self.thr1 = thr1
        self.thr2 = thr2
        self.thr3 = thr3

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']

        my_cards = [str(c) for c in hole_card]
        comm_card = [str(c) for c in community_card]

        wr = win_rate(self.np_simulations, self.arr, my_cards, comm_card)

        action = valid_actions[0]
        max_raise = valid_actions[2]['amount']['max']

        if wr > self.thr1:
            action = valid_actions[2]
            return action['action'], action['amount']['max']
        elif wr > self.thr2:
            action = valid_actions[2]
            return action['action'], action['amount']['min']
        elif wr > self.thr3:
            action = valid_actions[1]
            return action['action'], action['amount']
        else:
            action = valid_actions[0]
            return action['action'], action['amount']

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass