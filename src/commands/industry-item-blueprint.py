import os
import json

from application.factories import sdeManagerFromConfig
from base import eveClient, display
tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

MAX_WORKERS = 10


MARKET_LIST_FILE = os.path.normpath('resources/modules.json')

def run(itemId):
    sde = sdeManagerFromConfig()
    print(sde.getItemBlueprint(itemId) or "Blueprint não encontrada")
