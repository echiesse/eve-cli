import json
import os

from application.factories import sdeManagerFromConfig
from base import eveClient
from base.evecli import cli
from base.evecli.loader import getCharacterDataDir
from base.evecli.market import consolidateByTypeId
from support.algorithm import diffByKeyZip, groupListBy, groupDictBy, listToDict
from support.math import weightedAverage
from support.utils import jprint, showDateTime

sde = sdeManagerFromConfig()

from base.evecli.inventory import consolidateItems, inventoryFetch, inventorySave
import config


# TODO: Mover informações sobre localização e nomes de arquivos do evecli para um módulo de metadados (config) do projeto
INVENTORY_FILE_NAME = 'inventory.json'
INVENTORY_FILE = os.path.join(config.HOME_DIR, 'inventory.json')

def run(characterId):
    tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

    # Make sure the character's dir exists
    cli.ensureCharacterDir(characterId)
    return

    # Obtain character's inventory
    inventory = inventoryFetch(tranquility, characterId)
    characterDataDir = getCharacterDataDir(characterId)
    inventoryFile = os.path.join(characterDataDir, INVENTORY_FILE_NAME)
    inventorySave(inventory, inventoryFile)

    inventoryFilename = f'inventory-{showDateTime()}.json'
    inventoryPath = os.path.join(characterDataDir, inventoryFilename)
    inventorySave(inventory, inventoryPath)

    #jprint(inventory)

    # Obtain character's market orders
    # Obtain character's wallet transactions

    # These resources must be syncd at the same time. Meaning inventory and order must be obtained together.

    # Update the inventory average cost


    #buyOrders = list(filter(lambda o: o.get('is_buy_order') == True, MARKET_ORDERS))
    #newbuyOrders = list(filter(lambda o: o.get('is_buy_order') == True, NEW_MARKET_ORDERS))
    #update_inventory(INVENTORY, NEW_INVENTORY, buyOrders, newbuyOrders)

    '''
    ordersByTypeId = groupBy('type_id', [
        {
            'type_id': 1,
            'price': 10,
            'volume_remain': 41,
        },
        {
            'type_id': 1,
            'price': 12,
            'volume_remain': 5,
        },
        {
            'type_id': 2,
            'price': 5,
            'volume_remain': 1,
        },
    ])
    jprint(ordersByTypeId)
    '''


def update_inventory(
    inventory: list[dict],
    new_inventory: list[dict],
    buy_orders: list[dict],
    new_buy_orders: list[dict],
):
    inventory = consolidateItems(inventory)
    new_inventory = consolidateItems(new_inventory)

    inventory_diff = diffByKeyZip(new_inventory, inventory, 'quantity')

    # nenhuma ordem mudou -> repete valor antigo
    # uma das ordens mudou -> pegar dados da ordem que mudou
    # mais de uma ordem mudou ->

    marketOrders =  listToDict(buy_orders, 'order_id')
    newMarketOrders =  listToDict(new_buy_orders, 'order_id')

    ordersDiff = diffByKeyZip(newMarketOrders, marketOrders, 'volume_remain')
    groupedOrdersDiff = groupDictBy('type_id', ordersDiff)

    for type_id, item in new_inventory.items():
        order_deltas = []
        order_prices = []
        for buyOrder in groupedOrdersDiff.get(type_id) or []:
            order_deltas.append(abs(buyOrder['volume_remain']))
            order_prices.append(buyOrder['price'])

        item['average_cost'] = weightedAverage(
            [inventory[type_id]['average_cost'], *order_prices],
            [inventory[type_id]['quantity'], *order_deltas]
        )


    jprint(new_inventory)
