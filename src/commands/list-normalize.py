from application.resourceManager import *


def removeDuplicates(data, key = None):
    lookup = {}
    ret = []
    key = key or (lambda elem: elem)
    for item in data:
        k = key(item)
        if lookup.get(k) is None:
            ret.append(item)
            lookup[k] = item
    return ret


def run(resourceName):
    data = loadJsonResource(resourceName)
    if data is None:
        print(f'The resource "{resourceName}" could not be found.')
        exit(1)
    fixJsonResourceKeys(data)
    data = removeDuplicates(data, key = lambda elem: elem['id'])
    saveJsonResource(resourceName, data)
