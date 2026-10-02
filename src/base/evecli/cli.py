import json
import os
from pathlib import Path

from base import eveClient
from support.utils import ensureDir
import config


def ensureCharacterDir(characterId):
    path = os.path.join(config.EVECLI_DATA_DIR, characterId)
    if os.path.exists(path):
        return True

    # Verify if character exists:
    tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)
    if not tranquility.checkCharacterExists(characterId):
        return False

    # Create character dir:
    os.makedirs(path)
    return True


def createCharactersFile():
    with open(config.CHARACTERS_FILE, 'w') as char_file:
        json.dump({}, char_file)


def charactersFileExists():
    return Path(config.CHARACTERS_FILE).exists()


def scaffoldEvecliDir():
    ensureDir(config.EVECLI_DIR) # ~/.evecli/
    if not charactersFileExists():
        createCharactersFile()
