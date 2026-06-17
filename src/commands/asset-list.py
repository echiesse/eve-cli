import json
import pprint

from base import eveClient
tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

CHARACTER_ID = '2117307808'

#URL = 'https://esi.evetech.net/characters/{character_id}/assets'

def run(characterId):
    tranquility.authenticate()
    data = tranquility.getCharacterInventory(CHARACTER_ID)
    print(data)
