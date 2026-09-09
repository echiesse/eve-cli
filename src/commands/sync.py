import json
import os

from application.factories import sdeManagerFromConfig
from base.evecli.market import consolidateByTypeId
from support.algorithm import diffByKeyZip, groupListBy, groupDictBy, listToDict
from support.utils import jprint

sde = sdeManagerFromConfig()

from base.evecli.inventory import consolidateInventory
import config

INVENTORY_FILE = os.path.join(config.HOME_DIR, 'inventory.json')

INVENTORY = [
    {
        "id": 1050561597909,
        "type_id": 9836,
        "name": "Consumer Electronics",
        "quantity": 2000,
        "average_cost": 0
    },
    {
        "id": 1034471999330,
        "type_id": 15630,
        "name": "Republic Fleet Captain Insignia I",
        "quantity": 6,
        "average_cost": 100000
    },
    {
        "id": 1037135761304,
        "type_id": 25602,
        "name": "Thruster Console",
        "quantity": 1665,
        "average_cost": 0
    },
]

NEW_INVENTORY = [
    {
        "id": 1050561597909,
        "type_id": 9836,
        "name": "Consumer Electronics",
        "quantity": 2000,
        "average_cost": 0
    },
    {
        "id": 1034471999330,
        "type_id": 15630,
        "name": "Republic Fleet Captain Insignia I",
        "quantity": 10,
        "average_cost": 0
    },
    {
        "id": 1037135761304,
        "type_id": 25602,
        "name": "Thruster Console",
        "quantity": 1665,
        "average_cost": 0
    },
]

MARKET_ORDERS = [
    {
        "duration": 90,
        "escrow": 30699000.0,
        "is_buy_order": True,
        "is_corporation": False,
        "issued": "2026-06-03T03:12:01Z",
        "location_id": 60003760,
        "min_volume": 1,
        "order_id": 7347452265,
        "price": 80000.0,
        "range": "station",
        "region_id": 10000002,
        "type_id": 15630,
        "volume_remain": 45,
        "volume_total": 50
    },
    {
        "duration": 90,
        "escrow": 30699000.0,
        "is_buy_order": True,
        "is_corporation": False,
        "issued": "2026-06-03T03:12:01Z",
        "location_id": 60003760,
        "min_volume": 1,
        "order_id": 7347452266,
        "price": 81000.0,
        "range": "station",
        "region_id": 10000002,
        "type_id": 15630,
        "volume_remain": 45,
        "volume_total": 50
    },
]

NEW_MARKET_ORDERS = [
    {
        "duration": 90,
        "escrow": 30699000.0,
        "is_buy_order": True,
        "is_corporation": False,
        "issued": "2026-06-03T03:12:01Z",
        "location_id": 60003760,
        "min_volume": 1,
        "order_id": 7347452265,
        "price": 80000.0,
        "range": "station",
        "region_id": 10000002,
        "type_id": 15630,
        "volume_remain": 41,
        "volume_total": 50
    },
    {
        "duration": 90,
        "escrow": 30699000.0,
        "is_buy_order": True,
        "is_corporation": False,
        "issued": "2026-06-03T03:12:01Z",
        "location_id": 60003760,
        "min_volume": 1,
        "order_id": 7347452266,
        "price": 81000.0,
        "range": "station",
        "region_id": 10000002,
        "type_id": 15630,
        "volume_remain": 45,
        "volume_total": 50
    },
]

TRANSACTIONS = [
    {
        "client_id": 2116930837,
        "date": "2026-07-05T01:58:07Z",
        "is_buy": True,
        "is_personal": True,
        "journal_ref_id": 25774814738,
        "location_id": 60003760,
        "quantity": 4,
        "transaction_id": 6829676138,
        "type_id": 15630,
        "unit_price": 80000.0
    },
]

def run(characterId, stationId):
    # Obtain character's inventory
    # Obtain character's market orders
    # Obtain character's wallet transactions

    # These resources must be syncd at the same time. Meaning inventory and order must be obtained together.

    # Update the inventory average cost


    buyOrders = list(filter(lambda o: o.get('is_buy_order') == True, MARKET_ORDERS))
    newbuyOrders = list(filter(lambda o: o.get('is_buy_order') == True, NEW_MARKET_ORDERS))
    update_inventory(INVENTORY, NEW_INVENTORY, buyOrders, newbuyOrders)

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

def weightedAverage(values, weights):
    res = 0
    W = 0
    for i, value in enumerate(values):
        weight = weights[i]
        res += value * weight
        W += weight

    return res / W

def update_inventory(
    inventory: list[dict],
    new_inventory: list[dict],
    buy_orders: list[dict],
    new_buy_orders: list[dict],
):
    inventory = consolidateInventory(inventory)
    new_inventory = consolidateInventory(new_inventory)

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
