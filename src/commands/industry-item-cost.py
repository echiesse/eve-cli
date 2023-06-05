import os
import json

from application.factories import sdeManagerFromConfig
from base import eveClient, market
from base.blueprints import *

tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

MAX_WORKERS = 10


MARKET_LIST_FILE = os.path.normpath('resources/modules.json')

def run(itemId, regionId, solarSystemId, retries = 3):
    sde = sdeManagerFromConfig()
    # Obter a blueprint do item
    blueprint = sde.getItemBlueprint(itemId)
    bpo = BPO.fromJson(blueprint, 0, 0)

    # Calcular as quantidades necessárias de cada material com base na TE e ME da BP
    components = bpo.calcMaterialQuantity(1)

    # Obter os preços dos materiais necessários (Ler da lista de preços obticas do dia)
    prices = {}
    for id, quantity  in components.items():
        orders = tranquility.getMarketOrders(
            regionId,
            itemId = id,
            orderType = 'sell',
            retries = retries,
            solarSystemId = solarSystemId,
        )
        topSellOrder, sellPrice, actualSellCount = market.findTopOrder(orders, quantity)
        prices[id] = sellPrice * quantity

    # Calcular o custo do produto final
    print(sum(prices.values()))
