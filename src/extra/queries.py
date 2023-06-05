from base import eveClient

def getItemByName(datasource, itemName):
    queryResults = datasource.searchItem(itemName, strict=True)
    if len(queryResults.keys()) > 1:
        raise Exception('Error searching for "{itemName}": Query returned multiple values: {queryResults}')

    for category, itemIds in queryResults.items():
        if len(itemIds) > 1:
            raise Exception('Error searching for "{itemName}": Query returned multiple values: {queryResults}')
        return itemIds[0]
