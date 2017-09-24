from hyperopt.mongoexp import MongoTrials
import argparse
from hyperopt import STATUS_OK
import pymongo
from pymongo import MongoClient


def get_args():
    parser = argparse.ArgumentParser(description='Parameters optimization options.')
    parser.add_argument('experiment_name', type=str, help='Name of experiment.')
    parser.add_argument('--mongo_db', type=str, default='poker', help='Name of mongo database with results')
    parser.add_argument('--top_n', type=int, default=5, help='Number of top params')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    client = MongoClient('localhost', 1234)
    jobs = client[args.mongo_db]['jobs']
    all_results = jobs.find({'exp_key': args.experiment_name, 'result.status': STATUS_OK}).\
        sort('result.loss', pymongo.ASCENDING)
    
    total_trials = all_results.count()
    all_results = all_results[:args.top_n]
    print('total trials', total_trials)
    if total_trials > 0:
        for r in all_results:
            print('\nmean stack', -1*r['result']['loss'])
            print(r['result']['params'])
    else:
        print('no finished trials')
