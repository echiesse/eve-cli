import math
import multiprocessing as mp

import json
import pprint

from base import eveClient
tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

MAX_WORKERS = 10

def run(itemId):
    item = tranquility.getItem(itemId)
    pprint.pprint(item)
