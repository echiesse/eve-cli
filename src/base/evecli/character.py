import os

from attrs import define
from base import eveClient
from base.evecli.inventory import inventoryFetch, inventorySave
from base.evecli import cli
from support.utils import ensureDir, saveJson


@define
class Character:
    '''The relevant character's data for the cli application'''

    dataDir: str
    inventoryPath: str


def save_in_all_dirs(data: list|dict, filename: str, dirs: list):
    for path in dirs:
        path = os.path.join(path, filename)
        saveJson(data, path)


def fetchCharacterData(characterId):
    tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

    characterDataDir = cli.getCharacterDataDir(characterId)
    historicDataPath = cli.getCharacterTimestampedDataDir(characterId)
    ensureDir(historicDataPath)

    # Fetch inventory:
    inventory = inventoryFetch(tranquility, characterId)
    save_in_all_dirs(inventory, cli.INVENTORY_FILE_NAME, [characterDataDir, historicDataPath])

    # Fetch market orders:
    orders = tranquility.getCharacterOrders(characterId)
    save_in_all_dirs(orders, cli.MARKET_ORDERS_FILE_NAME, [characterDataDir, historicDataPath])
