import json
import sys


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


def jprint(d, indent = 2, file = sys.stdout):
    print(json.dumps(d, indent=indent), file=file)


def perror(*msg):
    print(*msg, file=sys.stderr)