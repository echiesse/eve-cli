import os

from attrs import define
from base import eveClient
from base.evecli.inventory import inventoryFetch, inventorySave
from base.evecli import cli
from support.utils import ensureDir


@define
class Character:
    '''The relevant character's data for the cli application'''

    dataDir: str
    inventoryPath: str


def fetchCharacterData(characterId):
    tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

    # Fetch inventory:
    inventory = inventoryFetch(tranquility, characterId)

    dataPath = cli.getCharacterDataDir(characterId)
    historicDataPath = cli.getCharacterTimestampedDataDir(characterId)
    ensureDir(historicDataPath)

    for path in [dataPath, historicDataPath]:
        inventoryPath = os.path.join(path, cli.INVENTORY_FILE_NAME)
        inventorySave(inventory, inventoryPath)

        # Fetch market orders: