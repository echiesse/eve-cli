import os
import json

from base import eveClient, display
tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

MAX_WORKERS = 10


MARKET_LIST_FILE = os.path.normpath('resources/materials.json')

def run(itemId):
    # Carregar o json com os itens atuais:
    marketItems = None
    with open(MARKET_LIST_FILE) as marketFile:
        marketItems = json.load(marketFile)

    # Verificar se o item já está na lista:
    for item in marketItems:
        if item['id'] == str(itemId):
            # => Item existe. Nada mais a fazer.
            return

    # Obter item atual:
    item = tranquility.getItem(itemId)
    entry = {
        'id': str(itemId),
        'name': item['name']
    }

    # Atualizar arquivo:
    marketItems.append(entry)
    marketItems.sort(key = lambda e: e['name'])
    updatedContents = json.dumps(marketItems, indent=4)
    with open(MARKET_LIST_FILE, 'w') as marketFile:
        marketFile.write(updatedContents)


    print(f'Adicionado Item "{display.showItem(item)}"')
