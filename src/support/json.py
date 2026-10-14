import json


def saveJson(data: dict, path, indent=None):
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=indent)


def loadJson(path):
    with open(path) as jsonfile:
        return json.load(jsonfile)