from najha import functional as f


class PriceTable:
    def __init__(self):
        self.items = []

    def __str__(self) -> str:
        return '\n'.join(map(str, self.items))

    def append(self, id, name, buyPrice, buyExtra, sellPrice, sellExtra):
        item = PriceTableItem(id, name, buyPrice, buyExtra, sellPrice, sellExtra)
        self.items.append(item)
        return item

    def appendFromOrders(self, id, name, orders, orderCountToConsider, orderType = 'all'):
        # Obter a maior ordem de venda dada a quantidade desejada:
        topSellOrder, sellPrice, actualSellCount = None, None, 0
        if orderType in ['sell', 'all']:
            topSellOrder, sellPrice, actualSellCount = findTopOrder(orders, orderCountToConsider)

        # Obter a menor ordem de compra dada a quantidade desejada:
        topBuyOrder, buyPrice, actualBuyCount = None, None, 0
        if orderType in ['buy', 'all']:
            topBuyOrder, buyPrice, actualBuyCount = findTopOrder(orders, orderCountToConsider, isBuyOrder=True)

        #Preparar resultados:
        if orderType in ['buy', 'all']:
            buyPrice, buyExtra = cleanPrice(buyPrice, topBuyOrder, actualBuyCount)

        if orderType in ['sell', 'all']:
            sellPrice, sellExtra = cleanPrice(sellPrice, topSellOrder, actualSellCount)

        return self.append(id, name, buyPrice, buyExtra, sellPrice, sellExtra)

    def getItem(self, id):
        for it in self.items:
            if it.id == int(id):
                return it
        return None

    @property
    def asdict(self):
        ret = {}
        for item in self.items:
            ret[item.id] = item.asdict
        return ret

    @property
    def asmap(self):
        ret = {}
        for item in self.items:
            ret[item.id] = item
        return ret


class PriceTableItem:
    def __init__(self, id, name, buyPrice, buyExtra, sellPrice, sellExtra):
        self.id = int(id)
        self.name = name
        self.buyPrice = buyPrice
        self.buyExtra = buyExtra
        self.sellPrice = sellPrice
        self.sellExtra = sellExtra

        self.averagePrice = None
        self.adjustedPrice = None
        self.estimatedItemValue = None
        self.installationCost = None
        self.materialCost = None
        self.bpCopyCost = None
        self.bpInventionCost = None

    @property
    def asdict(self):
        return {
            'name': self.name,
            'buyPrice': self.buyPrice,
            'buyExtra': self.buyExtra,
            'sellPrice': self.sellPrice,
            'sellExtra': self.sellExtra,
            'materialCost': self.materialCost,
            'averagePrice': self.averagePrice,
            'adjustedPrice': self.adjustedPrice,
            'estimatedItemValue': self.estimatedItemValue,
            'installationCost': self.installationCost,
            'bpCopyCost': self.bpCopyCost,
            'bpInventionCost': self.bpInventionCost,
        }

    @property
    def aslist(self):
        return [
            self.name,
            self.buyPrice,
            self.buyExtra,
            self.sellPrice,
            self.sellExtra,
            self.materialCost,
            self.averagePrice,
            self.adjustedPrice,
            self.estimatedItemValue,
            self.installationCost,
            self.bpCopyCost,
            self.bpInventionCost,
        ]

    def __str__(self):
        return '\t'.join(map(tostring, self.aslist))


def tostring(value):
    if type(value) is str:
        return value
    elif type(value) is float:
        return str(value).replace('.', ',')
    elif value is None:
        return ''
    else:
        return str(value)


def findTopOrder(orders, orderCountToConsider, isBuyOrder = False):
    topPrice = None
    actualCount = 0

    orders = f.map(lambda o: {
        'price': o['price'],
        'volume_remain': o['volume_remain'],
        }, filter(lambda o: (not isBuyOrder) ^ o['is_buy_order'], orders)
    )

    orders.sort(key = lambda o: o['price'], reverse = isBuyOrder)
    topOrder = None
    for order in orders:
        topOrder = order
        actualCount += order['volume_remain']
        if actualCount >= orderCountToConsider:
            topPrice = order['price']
            break

    return topOrder, topPrice, actualCount


def cleanPrice(price, topOrder, actualCount):
    extra = ''
    if topOrder is None:
        price = None
        extra = '(No order found)'
    elif price is None:
        price = topOrder['price']
        extra = f'(only {actualCount} orders)'

    return price, extra


if __name__ == '__main__':
    t = PriceTable()
    t.append('a', 'b', 'c', 'd', 'e')
    t.append('10', '20', 'c', 'd', 'e')
    print(t)
