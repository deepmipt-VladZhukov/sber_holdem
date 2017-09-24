import json
import sys

# from pypokerengine.players import BasePokerPlayer
from simple_players.fast_player import FastPlayer

# from pg_player import PgPlayer
# from aggressive_player import AggressivePlayer

if __name__ == '__main__':
    # best_params = [[1.9242502900271377, 1.4399491425139745], [1.2321173649628636, 0.9673304577212442], [1.8658490587197043, 0.7547097592834577], [2.676391331535975, 1.1787212710926933], [1.243768716573182, 0.4498130177301249], [1.0623347433558077, 1.088574116614371], 1.9480410366569125, [1.0659430651698094, 0.8509603297309563], [0.950456925151415, 0.40586569711277054]]
    best_params = [[1.9481293243008289, 0.4362033658202198], [1.2491870231565032, 0.9416326116942938], [1.3506296313945416, 0.4919079529906567], [0.9466710034156781, 0.5828291485762399], [1.849853264641812, 0.3356119983764777], [0.7148129386973219, 0.964579973742623], 0.714816455840688, [1.099807591650618, 0.6659023279665012], [0.8349211819999771, 0.7112103678281588]]

    player = FastPlayer(*best_params)

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
            player.set_uuid(data.get('uuid'))
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

