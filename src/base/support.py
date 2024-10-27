from contextlib import suppress
import json
import sys


def loadJson(filePath):
    data = None
    with suppress(FileNotFoundError):
        with open(filePath) as jsonFile:
            data = json.load(jsonFile)
    return data


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
