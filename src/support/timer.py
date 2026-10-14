import time


def timeit(fn):
    def wrapper(*args, **kwargs):
        t = time.time()
        ret = fn(*args, **kwargs)
        print(f't = {time.time() - t}')
        return ret
    return wrapper
