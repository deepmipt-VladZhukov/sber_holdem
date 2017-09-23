#!/usr/bin/env python
import sys
import hyperopt.mongoexp
import logging
from optimize import objective_fn


logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')
sys.exit(hyperopt.mongoexp.main_worker())
