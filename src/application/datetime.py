from datetime import datetime

from .formatters import formatDateTime


def showCurrentDateTime():
    return formatDateTime(datetime.now())