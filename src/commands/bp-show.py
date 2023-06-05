import json
import pprint

def run(blueprintId):
    blueprintId = int(blueprintId)
    filename = f'{blueprintId}.json'
    blueprint = None
    try:
        with open(f'resources\\sde\\extract\\blueprints\\{filename}') as bpFile:
            blueprint = json.load(bpFile)
        print(json.dumps(blueprint, indent=2))
    except FileNotFoundError:
        print(f'Arquivo não encontrado: {filename}')
