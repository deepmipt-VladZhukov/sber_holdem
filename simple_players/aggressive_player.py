from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import numpy as np

NB_SIMULATION = 500
FOLD = 0
CALL = 1
MIN_RAISE = 2
MAX_RAISE = 3
PRINT = False


class OtherPlayer:

    def __init__(self):
        self.actions = dict()
        self.actions['FOLD'] = 0
        self.actions['CALL'] = 0
        self.actions['RAISE'] = 0
        self.actions['ALLIN'] = 0
        self.actions_count = 0
        self.wins = []
        self.stack = 0


class AggressivePlayer(BasePokerPlayer):

    def __init__(self, p1=0.6, p2=1, p3=(1, 0.7),
                 p4=1.5, p5=1, p6=1, p7=1.1, p8=1):
        self.params = p1, p2, p3, p4, p5, p6, p7, p8
        self.start_stack = 0
        self.actions_in_game = 0
        self.global_stack = 0
        self.global_random = 0
        self.players_stats = dict()
        self.there_is_allin = False
        self.round = 0
        self.game_updates = 0
        self.previous_action = FOLD
        self.previous_street = None
        self.bank_history = []

    def declare_action(self, valid_actions, hole_card, round_state):

        stack = 0
        current_players = 0
        current_players_uuids = []
        for i in round_state['seats']:
            if self.uuid == i['uuid']:
                stack = i['stack']
            if i['state'] == 'participating':
                current_players+=1
                if self.uuid!= i['uuid']:
                    current_players_uuids.append(i['uuid'])

        if current_players < 2:
            current_players = 2
        community_card = round_state['community_card']

        win_rate = estimate_hole_card_win_rate(
            nb_simulation=NB_SIMULATION,
            nb_player=current_players,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        # is_my_stack_the_biggest = True
        #
        # for i in round_state['seats']:
        #     if i['stack'] > stack:
        #         is_my_stack_the_biggest = False

        bank = round_state['pot']['main']['amount']
        big_blind_amount = 2 * round_state['small_blind_amount']
        self.actions_in_game +=1

        if stack == 0:
            stack = 1

        on_the_big_blind = round_state['seats'][round_state['big_blind_pos']]['uuid'] == self.uuid
        on_the_small_blind = round_state['seats'][round_state['small_blind_pos']]['uuid'] == self.uuid

        action = self.select_action(win_rate, round_state, on_the_big_blind, on_the_small_blind, current_players,valid_actions, stack, current_players_uuids)
        self.previous_action = action
        if FOLD == action:
            if PRINT:
                print("{} fold".format(round_state['street']), self.actions_in_game)

            return valid_actions[0]['action'], valid_actions[0]['amount']
        elif CALL == action:
            if PRINT:
                print("{} call {}".format(round_state['street'], valid_actions[1]['amount']))

            return valid_actions[1]['action'], valid_actions[1]['amount']
        elif (MIN_RAISE == action or MAX_RAISE == action) and \
                (valid_actions[2]['amount']['min'] == -1 or valid_actions[2]['amount']['max'] == -1):
            if valid_actions[2]['amount']['min'] == -1:
                if PRINT:
                    print("{} call {}".format(round_state['street'],  valid_actions[1]['amount']))

            return valid_actions[1]['action'], valid_actions[1]['amount']

        elif MIN_RAISE == action:
            if PRINT:
                print("{} raise {}".format(round_state['street'], valid_actions[2]['amount']['min']))

            return valid_actions[2]['action'], valid_actions[2]['amount']['min']

        elif MAX_RAISE == action:
            if PRINT:
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
            else:
                self.players_stats[i['uuid']] = OtherPlayer()

        self.start_stack = stack
        self.global_stack = stack
        self.global_random = np.random.randint(10)

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.actions_in_game=0
        self.there_is_allin = False
        self.bank_history = []
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        self.game_updates+=1
        for i in round_state['seats']:
            if i['uuid'] != self.uuid:
                self.players_stats[i['uuid']].stack = i['stack']
        last_action = None
        if 'river' in round_state['action_histories']:
            last_action = round_state['action_histories']['river'][-1]
        elif 'turn' in round_state['action_histories']:
            last_action = round_state['action_histories']['turn'][-1]
        elif 'flop' in round_state['action_histories']:
            last_action = round_state['action_histories']['flop'][-1]
        elif 'preflop' in round_state['action_histories']:
            last_action = round_state['action_histories']['preflop'][-1]

        if last_action['uuid'] == self.uuid:
            return

        self.bank_history.append(round_state['pot']['main']['amount'])

        if last_action is not None and 'amount' in last_action and last_action['amount'] >= self.players_stats[last_action['uuid']].stack:
            self.players_stats[last_action['uuid']].actions['ALLIN'] += 1
            self.players_stats[last_action['uuid']].actions_count+=1
            self.there_is_allin = True
        else:
            self.players_stats[last_action['uuid']].actions[last_action['action']]+=1
            self.players_stats[last_action['uuid']].actions_count+=1

    def receive_round_result_message(self, winners, hand_info, round_state):
        stack = 0
        for i in round_state['seats']:
            if self.uuid == i['uuid']:
                stack = i['stack']
        if PRINT:
            print("actions in game",self.actions_in_game, "points", stack - self.global_stack)
        self.global_stack = stack
        self.round +=1

    def select_action(self, win_rate, round_state, on_the_big_blind, on_the_small_blind, current_players, valid_actions, stack, current_players_uuids):
        # count_allins = sum([self.players_stats[x].actions['ALLIN'] for x in current_players_uuids])
        # count_calls = sum([self.players_stats[x].actions['CALL'] for x in current_players_uuids]) + 1
        # count_raises = sum([self.players_stats[x].actions['RAISE'] for x in current_players_uuids]) + 1
        # count_folds = sum([self.players_stats[x].actions['FOLD'] for x in current_players_uuids]) + 1
        # count_actions = sum([self.players_stats[x].actions_count for x in current_players_uuids]) + 1

        action = FOLD

        p1, p2, p3, p4, p5, p6, p7, p8 = self.params

        # case 1
        if win_rate >= p1:
            action = MAX_RAISE

        # case 2
        elif win_rate >= p2 /current_players and valid_actions[1]['amount'] == 0:
            action = MIN_RAISE

        # case 3
        elif round_state['street'] == 'preflop' and win_rate >= p3[0] /current_players and valid_actions[1]['amount']/stack < p3[0]:
            action = CALL

        # case 4
        elif round_state['street'] == 'preflop' and win_rate >= p4 /current_players:
            action = CALL

        # case 5
        elif round_state['street'] == 'flop' and win_rate >= p5 /current_players:
            action = MIN_RAISE

        elif round_state['street'] == 'flop' and self.previous_action == MIN_RAISE and self.previous_street == 'flop':
            action = CALL

        # case 6
        elif round_state['street'] == 'turn' and win_rate >= p6 /current_players:
            action = MIN_RAISE

        elif round_state['street'] == 'turn' and self.previous_action == MIN_RAISE and self.previous_street == 'turn':
            action = CALL

        # case 7
        elif round_state['street'] == 'river' and win_rate >= p7 /current_players:
            action = MAX_RAISE

        # case 8
        elif round_state['street'] == 'river' and win_rate >= p8 /current_players:
            action = MIN_RAISE

        elif round_state['street'] == 'river' and self.previous_action == MIN_RAISE and self.previous_street == 'river':
            action = CALL

        elif valid_actions[1]['amount'] == 0:
            action = CALL

        else:
            action = FOLD

        self.previous_street = round_state['street']
        return action
