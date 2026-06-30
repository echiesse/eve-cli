import json
import pprint

from base import eveClient
tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

CHARACTER_ID = '2117307808'

#URL = 'https://esi.evetech.net/characters/{character_id}/assets'

'''
 {'is_singleton': True,
  'item_id': 1035415566648,
  'location_flag': 'Unlocked',
  'location_id': 1035489010147,
  'location_type': 'item',
  'quantity': 1,
  'type_id': 31154}
'''

def run(characterId):
    data = tranquility.getCharacterInventory(characterId)
    print('Name                                         | Quantity')
    for item in data[:10]:
        item_detail = tranquility.getItem(item['type_id'])
        print(f'{item_detail["name"]} | {item["quantity"]}')
