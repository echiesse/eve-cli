import json
import os

import requests

import base.authentication as auth
from utils import *

#https://esi.evetech.net/v1/markets/10000001/orders/?datasource=tranquility&order_type=sell&page=1
#https://esi.evetech.net/v3/universe/types/2048?datasource=tranquility&type_id=2048

ESI_HOST_URL = 'https://esi.evetech.net'
ESI_VERSION_PATH = 'latest'

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
        self.pageCount = pageCount # FIXME: Pagination changed


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
        self.clientId = auth.CLIENT_ID
        self.tokens = None
        self.configDir = os.path.normpath(os.path.expanduser('~/.evecli'))
        self.tokenPath = os.path.join(self.configDir, 'tokens.json')
        ensureDir(self.configDir)


    def saveTokens(self, tokens: auth.TokenResponse):
        with open(self.tokenPath, 'w') as tokenFile:
            tokenFile.write(tokens.as_json)

    def loadTokens(self):
        with open(self.tokenPath) as tokenFile:
            tokenContents = tokenFile.read()
            self.tokens = auth.TokenResponse.from_json(tokenContents)
            return self.tokens

    def login(self):
        self.tokens = auth.authenticate(self.clientId)
        self.saveTokens(self.tokens)

    def authenticate(self):
        try:
            self.refreshAccessToken()
        except Exception: # TODO: Catch correct exception
            self.login()

    def hasCredentials(self):
        return self.tokens != None

    '''
    def authenticate(self):
        # Subir o servidor para receber o callback
        # Enviar clientId e clientSecret para o endpoint de autorização
        # Receber o authorization code via callback
        # Derrubar o servidor
        # User o authorization code para obter tokens
    '''

    def refreshAccessToken(self):
        self.tokens = auth.refresh_access_token(self.tokens.refresh_token)
        self.saveTokens(self.tokens)


    def get(self, path, retries = 0, **params):
        shallUseAuth = params.get('useAuth') or False
        params['datasource'] = self.serverName
        filterStr = '&'.join([f'{k}={v}' for k, v in params.items()])
        url = f'{ESI_HOST_URL}/{ESI_VERSION_PATH}/{path}?{filterStr}'

        headers = {}
        #import pdb; pdb.set_trace() #<<<<<
        if shallUseAuth:
            if self.tokens is None:
                try:
                    self.loadTokens()
                except FileNotFoundError:
                    self.login()
            headers.update({
                'Authorization': f'Bearer {self.tokens.access_token}',
            })

        def performRequest(url):
            response = requests.get(url, headers=headers)
            print(response.status_code) #<<<<<
            if response.status_code == requests.codes.unauthorized:
                self.authenticate()
                headers.update({
                    'Authorization': f'Bearer {self.tokens.access_token}',
                })
                response = requests.get(url, headers=headers)
                response.raise_for_status()
            elif response.status_code >= 400:
                response.raise_for_status()
            return response

        response = retry(retries, performRequest, exceptions=requests.exceptions.HTTPError)(url)

        jsonResponse = response.content
        pageCount = int(response.headers.get('X-Pages') or 1)

        return ESIResponse(json.loads(jsonResponse), pageCount)

    def post(self, path, data):
        url = f'{ESI_HOST_URL}/{ESI_VERSION_PATH}/{path}'

        response = requests.post(url, data = data)
        response.raise_for_status()

        jsonResponse = response.content
        pageCount = int(response.headers.get('X-Pages') or 1)

        return ESIResponse(json.loads(jsonResponse), pageCount)

    def getSystem(self, systemId):
        response = self.get(f'universe/systems/{systemId}')
        return response.data

    def getSystems(self):
        response = self.get(f'universe/systems/')
        return response.data

    def getConstelation(self, constellationId):
        response = self.get(f'universe/constellations/{constellationId}')
        return response.data

    def getItem(self, itemId):
        response = self.get(f'universe/types/{itemId}')
        return response.data

    def getItemName(self, itemId):
        #https://esi.evetech.net/v3/universe/types/2048?datasource=tranquility&type_id=2048
        item = self.getItem(itemId)
        return item['name']

    def getNames(self, ids):
        assert isinstance(ids, list)
        data = str(ids)
        response = self.post(f'universe/names', data = data)
        return response.data

    def search(self, term, *, categories, strict=False, page = 1):
        path = 'search'
        categories_param = ",".join(categories)
        return self.get(path, search = term, categories = categories_param, strict = strict, page = page)


    def searchItem(self, itemName, *, strict=False, page = 1):
        return self.search(itemName, categories=['inventory_type'], strict=strict, page = page)


    def getMarketOrders(self, regionId, solarSystemId = None, itemId = None, orderType = 'all', retries = 0):
        path = f'markets/{regionId}/orders'

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
        path = 'markets/prices/'
        return self.get(path)


    def getIndustryCostIndices(self):
        path = 'industry/systems/'
        return self.get(path)


    def getIndustryCostIndicesDict(self):
        systems = self.getIndustryCostIndices().data
        result = {}
        for system in systems:
            systemData = {}
            for index in system['cost_indices']:
                systemData[index['activity']] = index['cost_index']
            result[system['solar_system_id']] = systemData

        return result


    def getCharacterInventory(self, characterId):
        response = self.get(f'characters/{characterId}/assets', useAuth = True)
        return response.data


    def getIndustryFacilities(self):
        path = '/industry/facilities/'
        return self.get(path)