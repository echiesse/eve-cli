from base import eveClient, display

from application.factories import sdeManagerFromConfig


MAX_WORKERS = 20


def run(searchTerm):
    sde = sdeManagerFromConfig()
    results = sde.searchItem(searchTerm)
    display.printItems(results)
