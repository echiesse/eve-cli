from base import eveClient

tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)


def testOrdersInRegion():
    res = tranquility.request('v1/markets/10000001/orders', order_type='sell', page=1)
    orders = res.json()
    for order in orders[:10]:
        print(order['price'])
        print(tranquility.getSystemName(order['system_id']))


def testOrdersInSystem():
    systemId = '30000185'
    orders = tranquility.getMarketOrders(0, systemId)
    print(f'{len(orders)} orders for: {tranquility.getSystemName(systemId)}')
    for order in orders:
        print(tranquility.getItemName(order['type_id']))
        print(order['price'])
        print(order['volume_remain'])
        print()