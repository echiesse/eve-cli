import json
import requests

#https://esi.evetech.net/v1/markets/10000001/orders/?datasource=tranquility&order_type=sell&page=1
#https://esi.evetech.net/v3/universe/types/2048?datasource=tranquility&type_id=2048

ESI_BASE_URL = 'https://esi.evetech.net'

class ServerNames:
    TRANQUILITY = 'tranquility'
    SINGULARITY = 'singularity'


CATEGORIES = {
    'AGENT': 'agent',
    'ALLIANCE': 'alliance',
    'CHARACTER': 'character',
    'CONSTELLATION': 'constellation',
    'CORPORATION': 'corporation',
    'FACTION': 'faction',
    'INVENTORY_TYPE': 'inventory_type',
    'REGION': 'region',
    'SOLAR_SYSTEM': 'solar_system',
    'STATION': 'station',
}


def paginatedRequest(requestFn, responseHandler):
    results = []

    pageResults = None
    currentPage = 1
    while pageResults != []:
        response = requestFn(currentPage)
        pageResults = responseHandler(response)
        results.extend(pageResults)

        if currentPage >= response.pageCount:
            break
        currentPage += 1

    return results


class ESIResponse:
    def __init__(self, data, pageCount):
        self.data = data
        self.pageCount = pageCount


def retry(count, fn, *, exceptions = Exception):
    def wrapper(*args, **kwargs):
        nonlocal count
        ret = None
        count += 1
        exception = None
        while count > 0:
            exception = None
            try:
                ret = fn(*args, **kwargs)
                break
            except exceptions as e:
                exception = e
                count -= 1

        if exception is not None:
            raise exception

        return ret

    return wrapper


class DataSource:
    def __init__(self, serverName):
        self.serverName = serverName

    def get(self, path, retries = 0, **params):
        params['datasource'] = self.serverName
        filterStr = '&'.join([f'{k}={v}' for k, v in params.items()])
        url = f'{ESI_BASE_URL}/{path}?{filterStr}'

        def performRequest(url):
            response = requests.get(url)
            response.raise_for_status()
            return response
        response = retry(retries, performRequest, exceptions=requests.exceptions.HTTPError)(url)

        jsonResponse = response.content
        pageCount = int(response.headers.get('X-Pages') or 1)

        return ESIResponse(json.loads(jsonResponse), pageCount)

    def post(self, path, data):
        url = f'{ESI_BASE_URL}/{path}'

        response = requests.post(url, data = data)
        response.raise_for_status()

        jsonResponse = response.content
        pageCount = int(response.headers.get('X-Pages') or 1)

        return ESIResponse(json.loads(jsonResponse), pageCount)

    def getSystem(self, systemId):
        response = self.get(f'latest/universe/systems/{systemId}')
        return response.data

    def getSystems(self):
        response = self.get(f'latest/universe/systems/')
        return response.data

    def getConstelation(self, constellationId):
        response = self.get(f'latest/universe/constellations/{constellationId}')
        return response.data

    def getItem(self, itemId):
        response = self.get(f'latest/universe/types/{itemId}')
        return response.data

    def getItemName(self, itemId):
        #https://esi.evetech.net/v3/universe/types/2048?datasource=tranquility&type_id=2048
        item = self.getItem(itemId)
        return item['name']

    def getNames(self, ids):
        assert isinstance(ids, list)
        data = str(ids)
        response = self.post(f'latest/universe/names', data = data)
        return response.data

    def search(self, term, *, categories, strict=False, page = 1):
        path = 'latest/search'
        categories_param = ",".join(categories)
        return self.get(path, search = term, categories = categories_param, strict = strict, page = page)


    def searchItem(self, itemName, *, strict=False, page = 1):
        return self.search(itemName, categories=['inventory_type'], strict=strict, page = page)


    def getMarketOrders(self, regionId, solarSystemId = None, itemId = None, orderType = 'all', retries = 0):
        path = f'latest/markets/{regionId}/orders'

        params = {
            'order_type': orderType,
        }
        if itemId is not None:
            params['type_id'] = itemId

        def handleResponse(response):
            filteredOrders = response.data
            if solarSystemId is not None:
                filteredOrders = list(filter(lambda o: int(o['system_id']) == int(solarSystemId), filteredOrders))
            return filteredOrders

        def performRequest(page):
            return self.get(path, retries = retries, page = page, **params)

        orders = paginatedRequest(performRequest, handleResponse)

        return orders


    def getPriceEstimates(self):
        path = f'latest/markets/prices/'
        return self.get(path)