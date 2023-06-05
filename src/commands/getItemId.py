import math
import multiprocessing as mp

from base import eveClient
tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

import najha.functional as f
MAX_WORKERS = 10


def printResults(results):
    for result in results:
        print(showResult(result))


def searchItem(name):
    return name, tranquility.searchItem(name, strict=True)

def run(inputFilePath):
    itemNames = None
    with open(inputFilePath) as inputFile:
        itemNames = inputFile.read()
        itemNames = f.filter(lambda s: s != '', f.map(str.strip, itemNames.split('\n')))

    workerCount = min(math.ceil(len(itemNames) / 2), MAX_WORKERS)
    print(f'Using {workerCount} workers') #<<<<<
    results = []
    with mp.Pool(workerCount) as p:
        results = p.map(searchItem, itemNames)


    for result in results:
        print(f"{result[1][0]['inventory_type'][0]}: {result[0]}")
