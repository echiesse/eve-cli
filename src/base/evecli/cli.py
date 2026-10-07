import json
import os
from pathlib import Path

from base import eveClient
from base.evecli.inventory import INVENTORY_FILE_NAME, inventoryFetch, inventorySave
from support.utils import ensureDir, showDateTime
import config


def getCharacterDataDir(characterId):
    return os.path.join(config.EVECLI_DATA_DIR, characterId)


def getCharacterHistoryAssetsDir(characterId):
    return os.path.join(getCharacterDataDir(characterId), 'history', 'assets')


def getCharacterTimestampedDataDir(characterId):
    return os.path.join(getCharacterHistoryAssetsDir(characterId), showDateTime())


def fetchCharacterData(characterId):
    tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)
    inventory = inventoryFetch(tranquility, characterId)

    dataPath = getCharacterDataDir(characterId)
    historicDataPath = getCharacterTimestampedDataDir(characterId)
    ensureDir(historicDataPath)

    for path in [dataPath, historicDataPath]:
        inventoryPath = os.path.join(path, INVENTORY_FILE_NAME)
        inventorySave(inventory, inventoryPath)


def ensureCharacterDir(characterId):
    character_data_path = getCharacterDataDir(characterId)
    if os.path.exists(character_data_path):
        return character_data_path

    # Verify if character exists:
    tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)
    if not tranquility.checkCharacterExists(characterId):
        return None

    # Create character's dir and its subdirs:
    os.makedirs(character_data_path)
    historyPath = os.path.join(character_data_path, 'history')
    os.mkdir(historyPath)
    os.mkdir(os.path.join(historyPath, 'prices'))
    os.mkdir(os.path.join(historyPath, 'assets'))

    return character_data_path


def createCharactersFile():
    with open(config.CHARACTERS_FILE, 'w') as char_file:
        json.dump({}, char_file)


def charactersFileExists():
    return Path(config.CHARACTERS_FILE).exists()


def scaffoldEvecliDir():
    ensureDir(config.EVECLI_DIR) # ~/.evecli/
    if not charactersFileExists():
        createCharactersFile()
