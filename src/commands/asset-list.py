from application.factories import sdeManagerFromConfig
from base.inventory import buildInventory, getItemNames, printInventory
from base import eveClient
tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)
sde = sdeManagerFromConfig()

CHARACTER_ID = '2117307808'


INDENT = '  '
def printDeep(val, level=0):
    indent = INDENT * level
    if isinstance(val, dict):
        for k, v in val.items():
            print(f'{indent}{k}')
            printDeep(v, level+1)
    else:
        print(f'{indent}{val}')


'''
 {'is_blueprint_copy': True,
  'is_singleton': True,
  'item_id': 1054757149132,
  'location_flag': 'Hangar',
  'location_id': 1044579290081,
  'location_type': 'item',
  'quantity': 1,
  'type_id': 10632},
 {'is_blueprint_copy': True,
  'is_singleton': True,
  'item_id': 1054757149167,
  'location_flag': 'Hangar',
  'location_id': 1044579290081,
  'location_type': 'item',
  'quantity': 1,
  'type_id': 10630}]
'''


def run(characterId):
    rawInventory = tranquility.getCharacterInventory(characterId)

    itemNameDict = getItemNames(tranquility, characterId, rawInventory)
    inventory = buildInventory(rawInventory)

    printInventory(inventory, itemNameDict)
