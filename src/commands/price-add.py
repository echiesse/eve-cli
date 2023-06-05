import sys
from application.resourceManager import *

from base import eveClient, display
from base.support import *

tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

RESOURCE_NAME = 'tracked_items'

def run(itemId):
    try:
        trackedItems = loadJsonResource(RESOURCE_NAME)
    except ResourceNotFoundException as e:
        print(e)
        sys.exit(1)

    if resourceHasItem(trackedItems, itemId):
        return

    # Obter item atual:
    item = tranquility.getItem(itemId)
    entry = {
        'id': str(itemId),
        'name': item['name']
    }

    addItemToResource(trackedItems, entry)
    saveJsonResource(RESOURCE_NAME, trackedItems)

    print(f'Adicionado Item "{display.showItem(item)}"')
