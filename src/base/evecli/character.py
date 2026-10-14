import os

from attrs import define
from base import eveClient
from base.evecli.inventory import rawInventoryFetch
from base.evecli import cli
from support.filesystem import ensureDir
from support.json import saveJson


@define
class Character:
    '''The relevant character's data for the cli application'''

    dataDir: str
    inventoryPath: str


def saveJsonInAllDirs(data: list|dict, filename: str, dirs: list):
    for path in dirs:
        path = os.path.join(path, filename)
        saveJson(data, path, indent=2)


def fetchCharacterData(characterId):
    tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

    characterDataDir = cli.getCharacterDataDir(characterId)
    historicDataPath = cli.genCharacterTimestampedDataDir(characterId)
    ensureDir(historicDataPath)

    # Fetch inventory:
    inventory = rawInventoryFetch(tranquility, characterId)
    saveJsonInAllDirs(inventory, cli.INVENTORY_FILE_NAME, [characterDataDir, historicDataPath])

    # Fetch market orders:
    orders = tranquility.getCharacterOrders(characterId)
    saveJsonInAllDirs(orders, cli.MARKET_ORDERS_FILE_NAME, [characterDataDir, historicDataPath])
