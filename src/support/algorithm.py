import support.functional as f

def difference(d1: dict, d2: dict):
    _d1 = d1.copy()
    _d2 = d2.copy()
    res = {}
    for k in d1:
        v1 = _d1.pop(k)
        v2 = d2.get(k)
        v2 = 0 if v2 is None else _d2.pop(k)

        res[k] = v1 - v2

    for k, v in _d2.items():
        res[k] = -v

    return res


def diffKey(d1: dict, d2: dict, key):
    res = d1.copy()
    res[key] = res.get(key, 0) - d2.get(key, 0)

    return res


def listToDict(l, keyField, reducer = None) -> dict:
    reducer = reducer or (lambda old, new: new)
    res = {}
    for newitem in l:
        key = newitem[keyField]
        if res.get(key) is None:
            res[key] = newitem
        else:
            #saved_item = res.setdefault(key, newitem)
            res[key] = reducer(res[key], newitem)

    return res


def groupListBy(key, items: list):
    res = {}
    for item in items:
        group = res.setdefault(item[key], [])
        group.append(item)
    return res


def groupDictBy(key, items: dict):
    res = {}
    for k, item in items.items():
        group = res.setdefault(item[key], [])
        group.append(item)
    return res


def sumField(field):
    def _sum(d1, d2):
        d1[field] += d2[field]
        return d1
    return _sum


def diffByKeyZip(d1, d2, item_key):
    return f.zip_with_d(
        lambda x, y: diffKey(x, y, item_key),
        d1,
        d2,
        lambda x: {**x, item_key:0}
    )
