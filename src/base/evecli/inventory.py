from __future__ import annotations

import math
import sys

from attrs import define, field

from application.factories import sdeManagerFromConfig
from base import eveClient
from support.algorithm import listToDict, sumField
from support.math import weightedAverage
from support.utils import jprint, loadJson

type Inventory = dict[str, Location]

sde = sdeManagerFromConfig()

INDENT = '  '

STATIONS = {
    60003760: 'Jita IV - Moon 4 - Caldari Navy Assembly Plant',
    60005203: 'Tama VII - Moon 9 - Republic Security Services Testing Facilities',
    60006427: 'Ikuchi VI - Moon 15 - Imperial Armaments Warehouse',
}

INDENT = '  '
@define
class Location:
    id: str
    items: dict[Item | Location] = field(init=False, factory=dict)

    def __str__(self):
        return self.show()

    def __getitem__(self, id):
        return self.items[id]

    def values(self):
        return self.items.values()

    def setItem(self, item: Item | Location):
        self.items[item.id] = item
        return self

    def show(self, level = 0):
        lines = []
        indent = INDENT * level
        for id, item in self.items.items():
            if isinstance(item, Location):
                lines.append(item.show(level+1))
            else:
                lines.append(f'{indent}{str(item)}')
        return '\n'.join(lines)


    @property
    def asdict(self):
        ret = {}
        for itemId, item in self.items.items():
            ret[itemId] = item.asdict
        return ret

    def mergeNames(self, itemNames: dict) -> Location:
        for item in self.values():
            if isinstance(item, Item):
                item.name = itemNames.get(item.id)
            else: # should be a Location
                item.mergeNames(itemNames)
        return self

    def onlyItems(self) -> list[Item]:
        items = list(filter(lambda x: isinstance(x, Item), self.values()))
        return items

@define
class Item:
    id: str
    typeId: str
    name: str
    quantity: int
    averageCost: float = field(init=False, default=0)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def update(self, quantity, unitCost):
        self.quantity += quantity
        self.averageCost = weightedAverage(
            [self.averageCost, unitCost],
            [self.quantity, quantity]
         )

    @property
    def totalCost(self):
        return self.averageCost * self.quantity

    @property
    def asdict(self):
        return {
            'id': self.id,
            'type_id': self.typeId,
            'name': self.name,
            'quantity': self.quantity,
            'average_cost': self.averageCost,
        }


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
            location.setItem(Item(item['item_id'], item['type_id'], '', item['quantity']))

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
                name = sde.getItemType(str(typeID))

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


def inventoryLoad(path):
    return loadJson(path)


def inventoryMergeNames(inventory: Inventory, itemNames: dict) -> Inventory:
    for itemId, location in inventory.items():
        location.mergeNames(itemNames)
    return inventory


def inventoryPrint(inventory, itemNames, level=0):
    indent = INDENT * level
    for itemId, contents in inventory.items():
        name = itemNames.get(itemId)
        if name is None:
            name = STATIONS.get(int(itemId))
        name = name or '?????'
        if not isLeafNode(contents): # branch node
            #name = location['name'] if location is not None else STATIONS.get(itemId) or 'TAMA ???'
            print(f'{indent}{name}:')
            inventoryPrint(contents, itemNames, level+1)
        else:
            print(f'{indent}{name} ({contents['quantity']})')


def inventoryFetch(apiclient, characterId):
    rawInventory = apiclient.getCharacterInventory(characterId)
    itemNameDict = getItemNames(apiclient, characterId, rawInventory)
    inventory = buildInventory(rawInventory)
    inventoryMergeNames(inventory, itemNameDict)
    return inventory