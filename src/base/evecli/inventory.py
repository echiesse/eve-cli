from __future__ import annotations

import json
import math
import sys

from attrs import define, field

from application.factories import sdeManagerFromConfig
from base import eveClient
from base.eve import Inventory, Item, Location
from support.algorithm import listToDict, sumField
from support.json import loadJson
from support.math import weightedAverage
from support.io import jprint


sde = sdeManagerFromConfig()


STATIONS = {
    60003760: 'Jita IV - Moon 4 - Caldari Navy Assembly Plant',
    60005203: 'Tama VII - Moon 9 - Republic Security Services Testing Facilities',
    60006427: 'Ikuchi VI - Moon 15 - Imperial Armaments Warehouse',
}

INDENT = '  '

def buildInventory(rawInventory: list) -> Inventory :
    t = _buildInventory(rawInventory)
    return _buildInventory(rawInventory, t)


def _buildInventory(rawInventory: list, nodeSet = None) -> Inventory :
    nodeSet = nodeSet or {}
    nonRoot = set()
    for item in rawInventory:
        locationId = item['location_id']
        itemId = item['item_id']
        location = nodeSet.setdefault(locationId, Location(locationId))
        if itemId in nodeSet:
            # Add existing node to the correct (existing) parent:
            location.setItem(nodeSet[itemId])
            nonRoot.add(itemId)
        else:
            # Add item to the just created node:
            try:
                location.setItem(Item(
                    item['item_id'],
                    item['name'],
                    item['type_id'],
                    item['type_name'],
                    item['quantity']
                ))
            except:
                print(item)
                raise

    # Filter non root items from the node set:
    inventory = {}
    for itemId, location in nodeSet.items():
        if itemId not in nonRoot:
            inventory[itemId] = location
    return inventory


def getItemNames(tranquility, characterId, rawInventory): # -> dict[id: name]
    # Get unique ids:
    itemDict = {}
    for item in rawInventory:
        itemDict[item['item_id']] = item
    ids = list(itemDict.keys())

    data = []
    n = len(ids)
    nreq = math.ceil(n / eveClient.MAX_API_ITEMS)
    for i in range(nreq):
        _items = tranquility.getCharacterAssetNames(
            characterId,
            ids[i * eveClient.MAX_API_ITEMS : (i + 1) * eveClient.MAX_API_ITEMS]
        )
        data.extend(_items)

    names = {}
    for item in data:
        # Use the type ID if the item does not have a name:
        itemId = item['item_id']
        name = item['name']
        if name == 'None':
            typeID = itemDict[itemId].get('type_id')
            if typeID is not None:
                name = sde.getTypeName(str(typeID))

            #print(item)
        id = item['item_id']
        names[id] = name
        #item['name'] = name

    return names


def consolidateItems(inventory: list[Item]):
    return listToDict(inventory, 'typeId', sumField('quantity'))


#-------------------------------------------------------------------------------
# Inventory functions:

def inventoryToDict(inventory: dict[str, Location]) -> dict:
    ret = {}
    for locationId, location in inventory.items():
        ret[locationId] = location.asdict
    return ret


def isLeafNode(node: Item|Location):
    return isinstance(node, Item)


def inventoryLoad(path) -> Inventory:
    rawInventory = loadJson(path)
    return buildInventory(rawInventory)


def inventoryMergeNames(inventory: Inventory, itemNames: dict) -> Inventory:
    for itemId, location in inventory.items():
        location.mergeNames(itemNames)
    return inventory


def inventoryPrint(inventory: Inventory, itemNames, level=0):
    indent = INDENT * level
    for locationId, location in inventory.items():
        name = itemNames.get(locationId)
        if name is None:
            name = STATIONS.get(int(locationId))
        name = name or '?????'
        print(location)


def rawInventoryFetch(apiclient, characterId) -> list[dict]:
    rawInventory = apiclient.getCharacterInventory(characterId)
    rawInventory = apiclient.fillAssetNames(rawInventory, characterId)
    rawInventory = rawInventoryFillTypeNames(rawInventory)

    return rawInventory


def rawInventoryFillTypeNames(rawInventory):
    for item in rawInventory:
        name = sde.getTypeName(str(item['type_id']))
        item['type_name'] = name
    return rawInventory