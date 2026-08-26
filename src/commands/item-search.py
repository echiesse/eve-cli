from base import eveClient

from application.factories import sdeManagerFromConfig
from base.evecli import display


MAX_WORKERS = 20


def run(searchTerm):
    sde = sdeManagerFromConfig()
    results = sde.searchItem(searchTerm)
    display.printItems(results)
