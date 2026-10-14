import json
import os

from base.evecli import display
from support.json import loadJson

RESOURCE_DIR = 'resources'

class ResourceNotFoundException(Exception):
    pass


def addItemToResource(resource, item):
    if resourceHasItem(resource, item['id']):
        return False
    resource.append(item)
    sortResource(resource)
    return True


def resourceHasItem(resource, itemId):
    for elem in resource:
        if elem['id'] == str(itemId):
            return True
    return False


def getResourcePath(resourceName):
    return os.path.join(RESOURCE_DIR, f'{resourceName}.json')


def loadJsonResource(resourceName):
    try:
        return loadJson(getResourcePath(resourceName))
    except FileNotFoundError:
        raise ResourceNotFoundException(f'The resource "{resourceName}" could not be found.')


def saveJsonResource(resourceName, data):
    jsonData = formatJsonResource(data)
    fileName = getResourcePath(resourceName)
    with open(fileName, 'w') as jsonFile:
        jsonFile.write(jsonData)


def sortResource(resource):
    resource.sort(key = lambda e: e['name'])


def formatJsonResource(jsonData):
    sortResource(jsonData)
    formattedJson = json.dumps(jsonData, indent=4)
    return formattedJson


def fixJsonResourceKeys(jsonData):
    for item in jsonData:
        if type(item['id']) == int:
            item['id'] = str(item['id'])

def showList(resourceName):
    items = loadJsonResource(resourceName)
    print(display.showList(items))
