import json
import os

from application.factories import sdeManagerFromConfig
from base.inventory import buildInventory, getItemNames, printInventory
from base import eveClient
from base.inventory import filterChildren
from utils import jprint, saveJson

tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)
sde = sdeManagerFromConfig()

CHARACTER_ID_AERO_SCRIPTER = '2117307808'
CHARACTER_ID_AKVO_SCRIPTER = '2116727652'

CHARACTER_ID = CHARACTER_ID_AERO_SCRIPTER

HOME_DIR = '..' # TODO: Use the user home in production
#HOME_DIR = os.path.expanduser('~/.evecli') # TODO: Use the user home in production

MARKET_ORDERS_FILE_NAME = 'market-orders.json'
MARKET_ORDERS_FILE = os.path.join(HOME_DIR, MARKET_ORDERS_FILE_NAME)

'''
id, type_name, quantity, current_cost
'''

JITA_4_4_STATION_ID = '60003760'

def run(characterId):
    orders = tranquility.getCharacterOrders(characterId, int(JITA_4_4_STATION_ID))
    saveJson(orders, MARKET_ORDERS_FILE, indent = 2)
    #orders = tranquility.getCharacterOrders(characterId)
    jprint(orders)
