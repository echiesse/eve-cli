import sys
import json

from base import eveClient

tranquility = eveClient.DataSource(eveClient.ServerNames.TRANQUILITY)

def run():
    system_ids = json.loads(tranquility.getSystems())
    systems = []
    for system_id in system_ids:
        system = tranquility.getSystem(system_id)
        systems.append(system)

    with open('eve_systems.json', 'w') as output_file:
        output_file.write('\n'.join(systems))

run()
