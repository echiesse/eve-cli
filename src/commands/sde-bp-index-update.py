from application.factories import sdeManagerFromConfig

def run():
    sdeClient = sdeManagerFromConfig()
    sdeClient.buildBlueprintTypeIdIndex()
