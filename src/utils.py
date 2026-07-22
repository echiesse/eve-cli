import os
import sys
import json
import time
from collections import deque
from datetime import datetime

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


def showDateTime():
    return datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')


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


def printDeep(val, level=0):
    indent = INDENT * level
    if isinstance(val, dict):
        for k, v in val.items():
            print(f'{indent}{k}')
            printDeep(v, level+1)
    else:
        print(f'{indent}{val}')


def perror(*msg):
    print(*msg, file=sys.stderr)



def timeit(fn):
    def wrapper(*args, **kwargs):
        t = time.time()
        ret = fn(*args, **kwargs)
        print(f't = {time.time() - t}')
        return ret
    return wrapper
