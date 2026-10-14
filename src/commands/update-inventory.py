import json
import os

from application.factories import sdeManagerFromConfig
from base.evecli.inventory import (
    consolidateItems,
    rawInventoryFetch,
)

from base import eveClient

from base.evecli.cli import getCharacterDataDir
from support.filesystem import ensureDir
import support.functional as f

from support.io import jprint
from application.datetime import showCurrentDateTime

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


JITA_4_4_STATION_ID = '60003760' # TODO: Remove so the user must always pass via command line arguments

def run(characterId, stationId):
    inventory = rawInventoryFetch(tranquility, characterId)
    stationInventory = inventory[int(stationId)]
    hangarItems = stationInventory.onlyItems()
    new_inventory = consolidateItems(hangarItems)

    characterDataDir = getCharacterDataDir(characterId)
    inventoryFile = os.path.join(characterDataDir, INVENTORY_FILE_NAME)
    #current_inventory = consolidateItems(inventoryLoad(inventoryFile))
    #new_inventory = consolidateItems(hangarItems)

    #inv_diff = diffByKeyZip(new_inventory, current_inventory, 'quantity')

    #jprint(inv_diff)

    ensureDir(characterDataDir)
    inventoryFilename = f'inventory-{stationId}-{showCurrentDateTime()}.json'
    inventoryPath = os.path.join(characterDataDir, inventoryFilename)

    _items = [item.asdict for item in hangarItems]
    with open(inventoryPath, 'w') as json_hangar:
        json.dump(_items, json_hangar, indent=2)

    with open(inventoryFile, 'w') as json_hangar:
        json.dump(_items, json_hangar, indent=2)
