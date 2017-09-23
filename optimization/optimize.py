import os
import sys
from pypokerengine.api.game import setup_config, start_poker
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(dir_path, '../simple_players'))
from honest_players_cpp_like import HonestPlayer, HonestPlayer2


def eval_player(num_evals=10, other_bots=[HonestPlayer(1000) for _ in range(8)],
                my_bot=HonestPlayer2(1000)):
    config = setup_config(max_round=10, initial_stack=1500, small_blind_amount=15)

    # add my player
    config.register_player(name="my_bot", algorithm=my_bot)
    # add other players
    for i, b in enumerate(other_bots):
        config.register_player(name="other_{}".format(i + 1), algorithm=b)

    result_dict = {}
    for _ in range(num_evals):
        game_result = start_poker(config, verbose=0)

        # add results
        for k in game_result['players']:
            result_dict.setdefault(k['name'], 0)
            result_dict[k['name']] += k['stack'] / num_evals

    return result_dict


if __name__ == '__main__':
    r = eval_player(1)
    print(r)
