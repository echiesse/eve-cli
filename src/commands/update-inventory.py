import json
import os

from application.factories import sdeManagerFromConfig
from base.evecli.inventory import (
    buildInventory,
    consolidateInventory,
    getItemNames,
    loadInventory,
)

from base import eveClient
from base.evecli.inventory import filterLeaf

from base.evecli.loader import getCharacterDataDir
import support.functional as f
from support.algorithm import diffByKeyZip

import config
from support.utils import ensureDir, jprint, showDateTime

CHARACTER_ID = config.CHARACTER_ID_AERO_SCRIPTER

tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)
sde = sdeManagerFromConfig()



INVENTORY_FILE_NAME = 'inventory.json'

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
            'type_id': item['type_id'],
            'name': itemNames.get(item['item_id']),
            'quantity': item['quantity'],
            'average_cost': 0,
        })

    return hangar



JITA_4_4_STATION_ID = '60003760' # TODO: Remove so the user must always pass via command line arguments

def run(characterId, stationId):
    rawInventory = tranquility.getCharacterInventory(characterId)

    itemNameDict = getItemNames(tranquility, characterId, rawInventory)
    inventory = buildInventory(rawInventory)
    #print(inventory)
    stationInventory = inventory[int(stationId)]
    hangarItems = filterLeaf(stationInventory)
    hangar = buildHangar(hangarItems, itemNameDict)

    characterDataDir = getCharacterDataDir(characterId)
    inventoryFile = os.path.join(characterDataDir, INVENTORY_FILE_NAME)
    current_inventory = consolidateInventory(loadInventory(inventoryFile))
    new_inventory = consolidateInventory(hangar)

    inv_diff = diffByKeyZip(new_inventory, current_inventory, 'quantity')

    #jprint(inv_diff)

    ensureDir(characterDataDir)
    inventoryFilename = f'inventory-{stationId}-{showDateTime()}.json'
    inventoryPath = os.path.join(characterDataDir, inventoryFilename)

    with open(inventoryPath, 'w') as json_hangar:
        json.dump(hangar, json_hangar, indent=2)

    with open(inventoryFile, 'w') as json_hangar:
        json.dump(hangar, json_hangar, indent=2)

    #printHangar(hangarItems, itemNameDict)
