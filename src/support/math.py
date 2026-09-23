

def weightedAverage(values, weights):
    res = 0
    W = 0
    for i, value in enumerate(values):
        weight = weights[i]
        res += value * weight
        W += weight

    return res / W
