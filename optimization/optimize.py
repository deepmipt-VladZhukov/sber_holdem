import os
import sys
from pypokerengine.api.game import setup_config, start_poker
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(dir_path, '..'))
from simple_players.honest_players_cpp_like import HonestPlayer, HonestPlayer2
from simple_players.random_player import RandomPlayer
from simple_players.aggressive_player import AggressivePlayer
from simple_players.caller_player import CallerPlayer
from simple_players.fast_player import FastPlayer
from simple_players.odd_player import OddPlayer

from hyperopt import hp, fmin, tpe, STATUS_OK
from hyperopt.mongoexp import MongoTrials
import argparse
from datetime import datetime
from multiprocessing import cpu_count
from subprocess import Popen


HYPEROPT_WORKER_CMD = './hp_worker.py --mongo=localhost:1234/{} --poll-interval=0.1 --workdir=tmp'


def eval_player(num_evals=5, other_bots=[HonestPlayer(1000) for _ in range(8)],
                my_bot=HonestPlayer2(1000)):
    config = setup_config(max_round=50, initial_stack=1500, small_blind_amount=15)
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


def objective_fn(params):
    other_bots = [OddPlayer(), HonestPlayer(100), HonestPlayer2(100), RandomPlayer(),
                  FastPlayer(), AggressivePlayer(), CallerPlayer(), RandomPlayer()]

    my_bot = FastPlayer(*params)
    r = eval_player(5, my_bot=my_bot, other_bots=other_bots)

    return {
        'loss': -1*r['my_bot'],
        'status': STATUS_OK,
        'all_results': r,
        'params': params
    }


def get_args():
    parser = argparse.ArgumentParser(description='Parameters optimization options.')
    parser.add_argument('--db_name', type=str, default='poker', help='Name of mongo database where to store data')
    parser.add_argument('--exp_name', type=str, default='exp_{}'.format(datetime.now().strftime("%d.%m.%Y-%H:%M")),
                        help='Experiment name.')
    parser.add_argument('--n_jobs', type=int,  default=cpu_count(), help='Number of workers. Negative for all cpus')
    parser.add_argument('--num_evals', type=int, default=10000000, help='Number of  evaluations')
    args = parser.parse_args()
    return args


SPACE = [[hp.uniform('p1_1', 1., 2.), hp.uniform('p1_2', 0.3, 1.5)],
         [hp.uniform('p2_1', 0.3, 1.5), hp.uniform('p2_2', 0.5, 1.5)],
         [hp.uniform('p3_1', 0.5, 2.), hp.uniform('p3_2', 0.2, 1.)],
         [hp.uniform('p4_1', 0.8, 3.), hp.uniform('p4_2', 0.3, 1.5)],
         [hp.uniform('p5_1', 0.5, 2.), hp.uniform('p5_2', 0.2, 1.)],
         [hp.uniform('p6_1', 0.3, 1.5), hp.uniform('p6_2', 0.3, 1.5)],
         hp.uniform('p7', 0.5, 2),
         [hp.uniform('p8_1', 0.5, 2.), hp.uniform('p8_2', 0.2, 1.)],
         [hp.uniform('p9_1', 0.3, 1.), hp.uniform('p9_2', 0.3, 1.5)],
]


if __name__ == '__main__':
    args = get_args()

    # create temp directory
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    print('start experiment {}'.format(args.exp_name))
    print('starting {} hyperopt workers'.format(args.n_jobs))
    with open('hyperopt_worker.log', 'a') as f:
        cmd = HYPEROPT_WORKER_CMD.format(args.db_name)
        for _ in range(args.n_jobs):
            Popen(cmd, stderr=f, shell=True)

    print('start minimization')
    trials = MongoTrials('mongo://localhost:1234/{}/jobs'.format(args.db_name), exp_key=args.exp_name)
    best = fmin(objective_fn, SPACE, algo=tpe.suggest, max_evals=args.num_evals, trials=trials)
    print(best)
