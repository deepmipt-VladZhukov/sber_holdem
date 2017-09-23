import os
import sys
from pypokerengine.api.game import setup_config, start_poker
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(dir_path, '../simple_players'))
from honest_players_cpp_like import HonestPlayer, HonestPlayer2
from hyperopt import hp, fmin, tpe
from hyperopt.mongoexp import MongoTrials
import argparse
import datetime
from multiprocessing import cpu_count
from subprocess import Popen


HYPEROPT_WORKER_CMD = './hp_worker.py --mongo=localhost:1234/{} --poll-interval=0.1 --workdir=tmp'


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

    return -1*result_dict['my_bot']


def objective_fn(params):
    r = eval_player(my_bot=HonestPlayer2(1000, params[0], params[1], params[2]))
    return r


def get_args():
    parser = argparse.ArgumentParser(description='Parameters optimization options.')
    parser.add_argument('--db_name', type=str, default='poker', help='Name of mongo database where to store data')
    parser.add_argument('--exp_name', type=str, default='exp_{}'.format(datetime.now().strftime("%d.%m.%Y-%H:%M")),
                        help='Experiment name.')
    parser.add_argument('--n_jobs', type=int,  default=cpu_count(), help='Number of workers. Negative for all cpus')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()

    # create temp directory
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    print 'starting {} hyperopt workers'.format(args.n_jobs)
    with open('hyperopt_worker.log', 'a') as f:
        cmd = HYPEROPT_WORKER_CMD.format(args.db_name)
        for _ in xrange(args.n_jobs):
            Popen(cmd.split(), stderr=f)

    space = [hp.uniform('thr1', 0.5, 1.), hp.uniform('thr2', 0.5, 1.), hp.uniform('thr3', 0.5, 1.)]
    trials = MongoTrials('mongo://localhost:1234/{}/jobs'.format(args.db_name), exp_key=args.exp_name)
    best = fmin(objective_fn, space, algo=tpe.suggest, max_evals=100)
    print(best)
