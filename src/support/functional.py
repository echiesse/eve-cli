
_map = map
_filter = filter

def map(fn, xs):
    return list(_map(fn, xs))


def filter(fn, xs):
    return list(_filter(fn, xs))


def zip_with(fn, xs, ys):
    ret = []
    for x, y in zip(xs, ys):
        ret.append(fn(x, y))
    return ret

def zip_with_d(fn, xs, ys, default_y_fn):
    ret = {}
    for k, x in xs.items():
        y = ys.get(k) or default_y_fn(x)
        ret[k] = fn(x, y)
    return ret