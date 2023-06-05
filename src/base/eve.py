
class Entity:
    pass

class SolarSystem(Entity):
    def __init__(self):
        pass
        # name
        # constellation

class Station(Entity):
    pass
    # name
    # solarSystem


class Item(Entity):
    ''' In Eve this is a "type" or "inventory_type" '''
    def __init__(self, name):
        self.name = name
