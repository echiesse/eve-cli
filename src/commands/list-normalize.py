from application.resourceManager import *

def run(resourceName):
    data = loadJsonResource(resourceName)
    if data is None:
        print(f'The resource "{resourceName}" could not be found.')
        exit(1)
    fixJsonResourceKeys(data)
    data = removeDuplicates(data, key = lambda elem: elem['id'])
    saveJsonResource(resourceName, data)
