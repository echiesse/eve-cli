import os
import sys
import json
from collections import deque

def getRegionById(regions, id):
    res = None
    for k, region in regions.items():
        if region['id'] == id:
            res = region
            break
    return res

'''
def splitPath(path, acc = None):
    if acc is None:
        acc = deque()
    dname, bname = os.path.split(path)
    acc.insert(0, bname)
    if dname != '':
        splitPath(dname, acc)

    return acc
'''

def ensureDir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok = True)


#def fromUnixPath(path):
#    parts = path.split('/')
#    return os.path.join(*parts)


INDENT = '    '
def pprint(val, ret = None, level = 0):
    if ret is None:
        ret = []

    if type(val) is list:
        ret[-1].append('[')
        for v in val:
            ret[-1].append(pprint(v), ret, level + 1)
        ret[-1].append(']')
    else:
        ret.extend(level * INDENT, str(val))


def perror(*msg):
    print(*msg, file=sys.stderr)