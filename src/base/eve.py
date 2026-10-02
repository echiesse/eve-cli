from __future__ import annotations

from attrs import define, field

from support.math import weightedAverage

type Inventory = dict[str, Location]


class SolarSystem:
    def __init__(self):
        pass
        # name
        # constellation


class Station:
    pass
    # name
    # solarSystem


@define
class Location:
    id: str
    items: dict[Item | Location] = field(init=False, factory=dict)
    INDENT = '  '

    def __str__(self):
        return self.show()

    def __getitem__(self, id):
        return self.items[id]

    def values(self):
        return self.items.values()

    def setItem(self, item: Item | Location):
        self.items[item.id] = item
        return self

    def show(self, level = 0):
        lines = []
        indent = self.INDENT * level
        for id, item in self.items.items():
            if isinstance(item, Location):
                lines.append(item.show(level+1))
            else:
                lines.append(f'{indent}{str(item)}')
        return '\n'.join(lines)


    @property
    def asdict(self):
        ret = {}
        for itemId, item in self.items.items():
            ret[itemId] = item.asdict
        return ret

    def mergeNames(self, itemNames: dict) -> Location:
        for item in self.values():
            if isinstance(item, Item):
                item.name = itemNames.get(item.id)
            else: # should be a Location
                item.mergeNames(itemNames)
        return self

    def onlyItems(self) -> list[Item]:
        items = list(filter(lambda x: isinstance(x, Item), self.values()))
        return items

@define
class Item:
    id: str
    typeId: str
    name: str
    quantity: int
    averageCost: float = field(init=False, default=0)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def update(self, quantity, unitCost):
        self.quantity += quantity
        self.averageCost = weightedAverage(
            [self.averageCost, unitCost],
            [self.quantity, quantity]
         )

    @property
    def totalCost(self):
        return self.averageCost * self.quantity

    @property
    def asdict(self):
        return {
            'id': self.id,
            'type_id': self.typeId,
            'name': self.name,
            'quantity': self.quantity,
            'average_cost': self.averageCost,
        }
