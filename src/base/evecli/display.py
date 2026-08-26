def showItem(result):
    idStr = str(result['type_id']).ljust(5)
    return f"{idStr} | {result['name']}"


def printItems(items):
    for result in items:
        print(showItem(result))


def showListItem(item):
    idStr = str(item['id']).ljust(5)
    return f"{idStr} | {item['name']}"


def showList(items):
    lines = []
    for item in items:
        lines.append(showListItem(item))
    return '\n'.join(lines)
