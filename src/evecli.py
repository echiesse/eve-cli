import math
import sys

from datetime import datetime
from importlib import import_module

import requests
from base import eveClient


class Options:
    pass


def run(*args, **kwargs):
    commandName = sys.argv[1]
    args = sys.argv[2:]
    processCommand(commandName, *args)


def processCommand(commandName, *args, **kwargs):
    try:
        command = import_module(f'commands.{commandName}')
        command.run(*args, **kwargs)
    except ModuleNotFoundError:
        print(f'Comando não encontrado: {commandName}')
        raise


def collectOptions(args):
    options = Options()
    options.verbose = '-v' in args
    return options


if __name__ == '__main__':
    options = collectOptions(sys.argv[1:])

    start = datetime.now()
    run()
    elapsedTime = datetime.now() - start
    if options.verbose:
        print(f'Tempo: {elapsedTime.total_seconds()}s')

