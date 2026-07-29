import json
import os

from base.market import PriceTable
from pathlib import Path


def run(*args):
    priceDataFileName = args[0]
    priceDataPath = os.path.join('price_history', priceDataFileName)
    jsonData = Path(priceDataPath).read_text()

    priceTable = PriceTable.fromJson(jsonData)

    print(priceTable)