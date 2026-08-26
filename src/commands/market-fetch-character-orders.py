import json
import os

from application.factories import sdeManagerFromConfig
from base.inventory import buildInventory, getItemNames, printInventory
from base import eveClient
from base.inventory import filterLeaf
from support.utils import ensureDir, jprint, saveJson, showDateTime

import config

CHARACTER_ID = config.CHARACTER_ID_AERO_SCRIPTER


tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)
sde = sdeManagerFromConfig()

MARKET_ORDERS_FILE_NAME = 'market-orders.json'
MARKET_ORDERS_FILE = os.path.join(config.EVECLI_DIR, MARKET_ORDERS_FILE_NAME)

'''
id, type_name, quantity, current_cost
'''

JITA_4_4_STATION_ID = '60003760'

def run(characterId, locationId):

    characterDataDir = os.path.join(config.EVECLI_DIR, 'data', characterId)
    ensureDir(characterDataDir)
    ordersFilename = f'market_orders-{locationId}-{showDateTime()}.json'
    ordersFilePath = os.path.join(characterDataDir, ordersFilename)

    orders = tranquility.getCharacterOrders(characterId, int(locationId))
    saveJson(orders, ordersFilePath, indent = 2)
    jprint(orders)
