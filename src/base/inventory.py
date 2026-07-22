import math

from application.factories import sdeManagerFromConfig
from base import eveClient
sde = sdeManagerFromConfig()

INDENT = '  '

STATIONS = {
    60003760: 'Jita IV - Moon 4 - Caldari Navy Assembly Plant',
    60005203: 'Tama VII - Moon 9 - Republic Security Services Testing Facilities',
    60006427: 'Ikuchi VI - Moon 15 - Imperial Armaments Warehouse',
}


def buildInventory(rawInventory):
    t = _buildInventory(rawInventory)
    return _buildInventory(rawInventory, t)


def _buildInventory(rawInventory, treeSet = None):
    treeSet = treeSet or {}
    nonRoot = set()
    for item in rawInventory:
        locationId = item['location_id']
        itemId = item['item_id']
        location = treeSet.setdefault(locationId, {})
        if itemId in treeSet:
            location[itemId] = treeSet[itemId]
            nonRoot.add(itemId)
        else:
            location[itemId] = item

    inventory = {}
    for itemId, item in treeSet.items():
        if itemId not in nonRoot:
            inventory[itemId] = item
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


def filterChildren(inventory):
    items = []
    for itemId, item in inventory.items():
        if isLeafNode(item):
            items.append(item)
    return items


def isLeafNode(node):
    return node.get('item_id') is not None


def printInventory(inventory, itemNames, level=0):
    indent = INDENT * level
    for itemId, contents in inventory.items():
        name = itemNames.get(itemId)
        if name is None:
            name = STATIONS.get(int(itemId))
        name = name or '?????'
        if not isLeafNode(contents): # branch node
            #name = location['name'] if location is not None else STATIONS.get(itemId) or 'TAMA ???'
            print(f'{indent}{name}:')
            printInventory(contents, itemNames, level+1)
        else:
            print(f'{indent}{name} ({contents['quantity']})')