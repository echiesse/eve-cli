from datetime import datetime


def formatDateTime(dt):
    return datetime.strftime(dt, '%Y%m%d_%H%M%S')