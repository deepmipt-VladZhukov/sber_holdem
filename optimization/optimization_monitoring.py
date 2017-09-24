from hyperopt.mongoexp import MongoTrials
import argparse
from hyperopt import STATUS_OK


def get_args():
    parser = argparse.ArgumentParser(description='Parameters optimization options.')
    parser.add_argument('experiment_name', type=str, help='Name of experiment.')
    parser.add_argument('--mongo_db', type=str, default='poker', help='Name of mongo database with results')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    trials = MongoTrials('mongo://localhost:1234/{}/jobs'.format(args.mongo_db), exp_key=args.experiment_name)

    all_results = trials.results
    total_trials = len([r for r in all_results if r['status'] == STATUS_OK])
    print('total trials', total_trials)
    if total_trials > 0:
        print('mean stack', -1*trials.best_trial['result']['loss'])
        print(trials.best_trial['result']['params'])
    else:
        print('no finished trials')
