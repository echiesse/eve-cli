
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


# TODO: Look at base.evecli.inventory.Item. Should it be here?
class Item(Entity):
    ''' In Eve this is a "type" or "inventory_type" '''
    def __init__(self, name):
        self.name = name
