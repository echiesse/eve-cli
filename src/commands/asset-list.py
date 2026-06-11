import json
import pprint

from base import eveClient
tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

CHARACTER_ID = '2117307808'

#URL = 'https://esi.evetech.net/characters/{character_id}/assets'

def run(characterId):
    #import pdb; pdb.set_trace() #<<<<<

    tranquility.authenticate()
    response = tranquility.get(f'characters/{CHARACTER_ID}/assets')
    print(response.data)
