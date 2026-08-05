import json
import os

from application.factories import sdeManagerFromConfig
from base.inventory import buildInventory, getItemNames, printInventory
from base import eveClient
from base.inventory import filterChildren

tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)
sde = sdeManagerFromConfig()

CHARACTER_ID_AERO_SCRIPTER = '2117307808'
CHARACTER_ID_AKVO_SCRIPTER = '2116727652'

CHARACTER_ID = CHARACTER_ID_AERO_SCRIPTER

HOME_DIR = '..' # TODO: Use the user home in production
#HOME_DIR = os.path.expanduser('~/.evecli') # TODO: Use the user home in production


INVENTORY_FILE = os.path.join(HOME_DIR, 'inventory.json')

'''
id, type_name, quantity, current_cost
'''

def printHangar(hangar, itemNames):
    for item in hangar:
        name = itemNames.get(item['item_id'])
        name = name or '?????'
        print(f'{name} ({item['quantity']})')

def buildHangar(items, itemNames):
    hangar = []
    for item in items:
        hangar.append({
            'id': item['item_id'],
            'name': itemNames.get(item['item_id']),
            'quantity': item['quantity'],
            'average_cost': 0,
        })

    return hangar



def run(characterId, stationId):
    rawInventory = tranquility.getCharacterInventory(characterId)

    itemNameDict = getItemNames(tranquility, characterId, rawInventory)
    inventory = buildInventory(rawInventory)
    #print(inventory)
    stationInventory = inventory[int(stationId)]
    hangarItems = filterChildren(stationInventory)
    hangar = buildHangar(hangarItems, itemNameDict)
    with open(INVENTORY_FILE, 'w') as json_hangar:
        json.dump(hangar, json_hangar, indent=2)
    #printHangar(hangarItems, itemNameDict)
