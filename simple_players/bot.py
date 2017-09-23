import sys
import json
import numpy as np

from pypokerengine.players import BasePokerPlayer

from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate


class MyPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"
    stack = 1500
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        NB_SIMULATION = 75
        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
                nb_simulation=NB_SIMULATION,
                nb_player=self.nb_player,
                hole_card=gen_cards(hole_card),
                community_card=gen_cards(community_card)
                )
        if win_rate >= 1.0 / self.nb_player:
            i = 2
            curr_stack = 0
            for player in round_state['seats']:
                if player['name'] == 'lantier':
                    curr_stack = player['stack']
            if curr_stack >= 1700:
                i = 0
            call_action_info = valid_actions[i]
            action, amount = call_action_info["action"], call_action_info["amount"]
            if i == 2:
                amount = amount["min"] + round((amount["max"] - amount["min"])/2)
            if amount == -1:
                i = 1
                call_action_info = valid_actions[i]
                action, amount = call_action_info["action"], call_action_info["amount"]
        else:
            i = 0
            curr_stack = 1500
            
            for player in round_state['seats']:
                if player['name'] == 'lantier':
                    curr_stack = player['stack']

            if valid_actions[1]["amount"] == 0 or (round_state['street'] == 'preflop' and \
                                                   self.stack - curr_stack == 2*round_state['small_blind_amount']):
                i = 1
            
            call_action_info = valid_actions[i]
            action, amount = call_action_info["action"], call_action_info["amount"]
        return action, amount

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


if __name__ == '__main__':

    player = MyPlayer()

    while True:
        line = sys.stdin.readline().rstrip()
        if not line:
           break
        event_type, data = line.split('\t', 1)
        data = json.loads(data)

        if event_type == 'declare_action':
            action, amount = player.declare_action(data['valid_actions'], data['hole_card'], data['round_state'])
            sys.stdout.write('{}\t{}\n'.format(action, amount))
            sys.stdout.flush()
        elif event_type == 'game_start':
            player.receive_game_start_message(data)
        elif event_type == 'round_start':
            player.receive_round_start_message(data['round_count'], data['hole_card'], data['seats'])
        elif event_type == 'street_start':
            player.receive_street_start_message(data['street'], data['round_state'])
        elif event_type == 'game_update':
            player.receive_game_update_message(data['new_action'], data['round_state'])
        elif event_type == 'round_result':
            player.receive_round_result_message(data['winners'], data['hand_info'], data['round_state'])
        else:
            raise RuntimeError('Bad event type "{}"'.format(event_type))