import math
import multiprocessing as mp

import najha.functional as f

from base import eveClient, display

MAX_WORKERS = 10


def run(searchTerm, categories=None):
    tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

    if categories is None:
        categories = eveClient.CATEGORIES.values()
    else:
        categories = f.map(str.strip, categories.split(','))

    def requestItems(page):
        return tranquility.search(searchTerm, categories=categories, page = page)

    def handleResponse(response):
        reponse = tranquility.search(searchTerm, categories=categories)
        currentItems = reponse.data
        results = []
        for category, itemIds in currentItems.items():
            names = tranquility.getNames(itemIds)
            results.extend(names)
        return results

    results = eveClient.paginatedRequest(requestItems, handleResponse)

    dresults = {}
    for item in results:
        if dresults.get(item['category']) is None:
            dresults[item['category']] = []
        dresults.get(item['category']).append(item)

    for category, items in dresults.items():
        print(f'{category}:')
        for item in items:
            print(f'    {item["id"]} | {item["name"]}')
        print()


