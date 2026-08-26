import os

import config

#from character import Character

def getCharacterDataDir(characterId):
    return os.path.join(config.EVECLI_DIR, 'data', characterId)


#def loadCharacter(characterId):
#    characterDataDir = getCharacterDataDir(characterId)
#    ensureDir(characterDataDir)
#    inventoryPath = os.path.join(characterDataDir, inventoryFilename)
