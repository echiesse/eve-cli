from base import eveClient

from najha import functional as f

def searchItem(searchTerm):
    tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

    def requestItems(page):
        return tranquility.searchItem(searchTerm, page = page)

    def handleResponse(response):
        currentItems = response.data
        results = []
        for category, itemIds in currentItems.items():
            names = tranquility.getNames(itemIds)
            results.extend(f.map(lambda item: {
                'type_id': item['id'],
                'name': item['name']
            } , names))
        return results

    results = eveClient.paginatedRequest(requestItems, handleResponse)
    return results
