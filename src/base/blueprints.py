import json
import math

class Blueprint:
    def __init__(self, data):
        self.id = data['blueprintTypeID']
        self.data = data
        self._components = {item['typeID']: item['quantity'] for item in self.data['activities']['manufacturing']['materials']}

    @classmethod
    def fromJson(cls, jsondata):
        data = json.loads(jsondata)
        bp = cls(data)
        return bp

    @property
    def name(self):
        return self.data['name']

    @property
    def components(self):
        return self._components

    @property
    def runOutputCount(self):
        return self.data['activities']['manufacturing']['products'][0]['quantity']

    @property
    def runCycleTime(self):
        return self.data['activities']['manufacturing']['time']

    @property
    def maxProductionLimit(self):
        return self.data['maxProductionLimit']


class BPO(Blueprint):
    MAX_MATERIAL_EFFICIENCY = 10
    MAX_TIME_EFFICIENCY = 20

    def __init__(self, data, materialEfficiency, timeEfficiency):
        if materialEfficiency > self.MAX_MATERIAL_EFFICIENCY or materialEfficiency < 0:
            raise ValueError(f'Material efficiency must be between 0 and {self.MAX_MATERIAL_EFFICIENCY}')
        if timeEfficiency > self.MAX_TIME_EFFICIENCY or timeEfficiency < 0:
            raise ValueError(f'Time efficiency must be between 0 and {self.MAX_TIME_EFFICIENCY}')

        super().__init__(data)
        self.materialEfficiency = materialEfficiency
        self.timeEfficiency = timeEfficiency

    @classmethod
    def fromJson(cls, data, materialEfficiency, timeEfficiency):
        return cls(data, materialEfficiency, timeEfficiency)

    @classmethod
    def fromBlueprint(cls, bp, materialEfficiency, timeEfficiency):
        return cls(bp.data, materialEfficiency, timeEfficiency)

    @property
    def me(self):
        '''Material efficiency as a ratio instead of a percentage'''
        return self.materialEfficiency / 100

    @me.setter
    def me(self, value):
        self.materialEfficiency = round(value * 100)

    @property
    def te(self):
        '''Time efficiency as a ratio instead of a percentage'''
        return self.timeEfficiency / 100

    @te.setter
    def te(self, value):
        self.timeEfficiency = round(value * 100)

    def runCycleTime(self, industryLevel = 0, advancedIndustryLevel = 0):
        '''Calculates the real time necessary to build an item considering time efficiency and player skills.

        Time reductions are calculated per group, meaning BP time efficiency is one group, industry skill is another
        group and advanced industry skill another one.

        The increase in the percentage is linear within one group. For example, if the player has level 3 industry, the
        discount related to that skill will be 3 * 0.04 = 0.12.

        The discount of each group is applied on top of each other, which leads to the expression:

        realTime = baseTime * (1 - TE) * (1 - IndustryLevel * 0.04) * (1 - AdvancedIndustryLevel * 0.03)
        '''
        return super().runCycleTime * (1 - self.te) * (1 - industryLevel * 0.04) * (1 - advancedIndustryLevel * 0.03)

    def calcMaterialQuantity(self, runCount):
        ret = {}
        for id, quantity in self.components.items():
            ret[id] = runCount * quantity
            if quantity > 1:
                ret[id] *= (1 - self.me)
            ret[id] = math.ceil(ret[id])
        return ret


class BPC(BPO):
    def __init__(self, data, materialEfficiency, timeEfficiency, remainingRunCount):
        super().__init__(data, materialEfficiency, timeEfficiency)
        self.remainingRunCount = remainingRunCount

    @classmethod
    def fromBPO(cls, bpo, remainingRunCount):
        return cls(bpo.data, bpo.materialEfficiency, bpo.timeEfficiency, remainingRunCount)


if __name__ == '__main__':
    jsonData = None
    with open('resources/sde/extract/blueprints/10632.json') as bpFile:
        jsonData = bpFile.read()
    bp = Blueprint.fromJson(jsonData)
    bpo = BPO.fromBlueprint(bp, 0, 2)
    #print(bp.data)
    print(bpo.components)
    print(bpo.runOutputCount)
    print(bp.runCycleTime)
    print(bpo.runCycleTime(5, 4))