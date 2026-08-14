

import json
import os

from application.factories import sdeManagerFromConfig
from base.inventory import buildInventory, getItemNames, printInventory
from base import eveClient
from base.inventory import filterChildren
from utils import jprint

import config

tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)
sde = sdeManagerFromConfig()

TRANSACTION_FILE = os.path.join(config.HOME_DIR, 'transactions.json')


def run(characterId):
    print(os.getcwd())
    transations = tranquility.getCharacterTransations(characterId)
    with open(TRANSACTION_FILE, 'w') as transaction_file:
        json.dump(transations, transaction_file, indent=2)

    #jprint(transations)