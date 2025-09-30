import os
import sys

import multiprocessing as mp

from application.factories import sdeManagerFromConfig
from base import eveClient, market
from base.blueprints import *
from base.support import loadJson
from extra.queries import *
from utils import *

ORDER_TYPES = ['sell', 'buy', 'all']
MAX_WORKERS = 10

tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)
sde = sdeManagerFromConfig()


def findRegion(*, regionId = None, regionName = None):
    regions = loadJson(os.path.join('resources', 'regions.json'))
    region = {'id': None, 'name': None}
    if regionId is not None:
        region['id'] = regionId
        region = getRegionById(regionId) or region
    else:
        regionName = regionName or "The Forge"
        region = regions.get(regionName)
        if region is None:
            print(f'Could not find region {region}')
            exit(1)
    return region

def printHeader(regionName, regionId, orderCountToConsider):
    print(f'Regiao: {regionName} (ID: {regionId})')
    print(f'Ordens consideradas: {orderCountToConsider}')
    print()


def worker_getOrders(args):
    item, regionId, orderType, retries, optionalParams = args
    return item['id'], item['name'], tranquility.getMarketOrders(
        regionId,
        itemId = item['id'],
        orderType = orderType,
        retries = retries,
        **optionalParams
    )


def getPricesFromESI(items, regionId, orderCountToConsider, orderType, retries, **optionalParams):
    priceTable = market.PriceTable()

    orderMap = []
    with mp.Pool(MAX_WORKERS) as pool:
        orderMap = pool.map(
            worker_getOrders,
            map(
                lambda item: (item, regionId, orderType, retries, optionalParams),
                items
            )
        )

    for id, name, orders in orderMap:
        item = priceTable.appendFromOrders(id, name, orders, orderCountToConsider, orderType)

    return priceTable


def getInGameEstimatePrices(client):
    estimates = client.getPriceEstimates().data
    return {item['type_id']: item for item in estimates }


def run(*args):
    # https://esi.evetech.net/latest/markets/10000002/orders/?datasource=tranquility&order_type=sell&page=1&type_id=25600

    itemsListFile = None
    orderCountToConsider = 3500
    regionName = None
    regionId = None
    solarSystemName = None
    shallPrintHeader = True
    orderType = 'sell'
    retries = 0

    for arg in args:
        if arg.startswith('region='):
            _, regionName = arg.split('=')
        elif arg.startswith('region-id='):
            _, regionId = arg.split('=')
            regionId = int(regionId)
        elif arg.startswith('order-count='):
            _, orderCountToConsider = arg.split('=')
            orderCountToConsider = int(orderCountToConsider)
        elif arg.startswith('order-type='):
            _, orderType = arg.split('=')
            if orderType not in ORDER_TYPES:
                print(f'order-type must be one of "sell", "buy" or "all". "sell" is the default')
                exit(0)
        elif arg.startswith('system='):
            _, solarSystemName = arg.split('=')
        elif arg.startswith('retries='):
            _, retries = arg.split('=')
            retries = int(retries)
        elif arg == 'noheader':
            shallPrintHeader = False
        else:
            itemsListFile = arg

    if itemsListFile is None:
        print('É obrigatório especificar o arquivo de input com os itens')
        exit(0)

    optionalParams = {}

    # Get region (Ex: The Forge, Domain, etc):
    region = findRegion(regionId = regionId, regionName = regionName)

    # TODO: Warning! I want to stay in the same station, so the region orders may not be the best option. <<<<<
    # Get Solar System:
    solarSystems = loadJson(os.path.join('resources', 'systems.json'))
    solarSystem = solarSystems.get(solarSystemName)
    if solarSystem is not None:
        optionalParams['solarSystemId'] = solarSystem['id']

    if shallPrintHeader:
        printHeader(region["name"], region["id"], orderCountToConsider)

    # Obtain "System Cost Index"
    systemCostIndices = tranquility.getIndustryCostIndicesDict()
    systemCostIndex = systemCostIndices.get(solarSystem['id'], {}).get('manufacturing')
    print(f'System Cost Index: {systemCostIndex}', file=sys.stderr)

    # Obtain prices of the materials:
    items = loadJson(itemsListFile)
    items.sort(key = lambda m: m['name'])
    priceTable = getPricesFromESI(items, region['id'], orderCountToConsider, orderType, retries, **optionalParams)

    inGameEstimatePrices = getInGameEstimatePrices(tranquility)
    for tableItem in priceTable.items:
        inGameEstimates = inGameEstimatePrices.get(tableItem.id)
        if inGameEstimates is not None:
            try:
                tableItem.averagePrice = inGameEstimates['average_price']
                tableItem.adjustedPrice = inGameEstimates['adjusted_price']
            except Exception as e:
                perror(f'Error processing item: {tableItem.name}')
                perror(f'{type(e).__name__}: {e}')

    # Taxes (They are fixed for NPC stations):
    facilityBonuses = 1
    facilityTax = 0.0025
    sccSurcharge = 0.04


    # Calculate cost of industry items:
    for item in items:
        itemId = item['id']
        # Obtain item's blueprint:
        try:
            blueprint = sde.getItemBlueprint(itemId)
        except Exception:
            continue

        if blueprint is None:
            continue

        bpo = BPO(blueprint, 0, 0) # TODO: Consider BPOs with better ME and TE
        currentProduct = priceTable.getItem(itemId)
        components = bpo.calcMaterialQuantity(1)

        # Calculate components cost:
        componentPrices = {}
        eiv = 0
        succeded = True
        for id, quantity in components.items():
            id = int(id)
            component = priceTable.getItem(id)
            if component is None:
                print(f'Preço não encontrado para componente de id "{id}"', file=sys.stderr) #<<<<<
                succeded = False
                break
            else:
                if component.sellPrice is None:
                    perror(f'"Sell Price" não encontrado para componente de id "{id}" ({component.name})')
                    succeded = False
                    break
                componentPrices[id] = component.sellPrice * quantity
                if component.adjustedPrice is None:
                    perror(f'"Adjusted Price" não encontrado para componente de id "{id}" ({component.name})')
                    succeded = False
                    break
                eiv += component.adjustedPrice * quantity

        if succeded:
            currentProduct.materialCost = sum(componentPrices.values()) / bpo.runOutputCount
            currentProduct.estimatedItemValue = eiv
            currentProduct.installationCost = eiv * (systemCostIndex * facilityBonuses + facilityTax + sccSurcharge) / bpo.runOutputCount

    # Show table:
    print(priceTable)
