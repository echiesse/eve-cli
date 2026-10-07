import json
import os
from pathlib import Path

from base import eveClient
from support.utils import ensureDir, showDateTime

#-------------------------------------------------------------------------------
# Contants:

SDE_URL = 'https://developers.eveonline.com/static-data/eve-online-static-data-latest-yaml.zip'
SDE_DIR = 'resources/sde/extract'
SDE_ARCHIVE_NAME = 'sde.zip'

# TODO: Use the user home in production
HOME_DIR = os.path.join(os.path.dirname(os.getcwd()), 'home')
#HOME_DIR = os.path.expanduser('~')
EVECLI_DIR = os.path.join(HOME_DIR, '.evecli')
EVECLI_DATA_DIR = os.path.join(EVECLI_DIR, 'data')

CHARACTERS_FILE = os.path.join(EVECLI_DATA_DIR, 'characters.json')

INVENTORY_FILE_NAME = 'inventory.json'
INVENTORY_FILE = os.path.join(HOME_DIR, INVENTORY_FILE_NAME)

MARKET_ORDERS_FILE_NAME = 'market_orders.json'
MARKET_ORDERS_FILE = os.path.join(HOME_DIR, MARKET_ORDERS_FILE_NAME)

#-------------------------------------------------------------------------------

def getCharacterDataDir(characterId):
    return os.path.join(EVECLI_DATA_DIR, characterId)


def getCharacterHistoryAssetsDir(characterId):
    return os.path.join(getCharacterDataDir(characterId), 'history', 'assets')


def getCharacterTimestampedDataDir(characterId):
    return os.path.join(getCharacterHistoryAssetsDir(characterId), showDateTime())


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
    with open(CHARACTERS_FILE, 'w') as char_file:
        json.dump({}, char_file)


def charactersFileExists():
    return Path(CHARACTERS_FILE).exists()


def scaffoldEvecliDir():
    ensureDir(EVECLI_DIR) # ~/.evecli/
    if not charactersFileExists():
        createCharactersFile()
