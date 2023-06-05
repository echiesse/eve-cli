import sys

from application import resourceManager


def run(resourceType):
    try:
        resourceManager.showList(resourceType)
    except resourceManager.ResourceNotFoundException:
        print(f'O recurso {resourceType} não foi encontrado.')


if __name__ == '__main__':
    run(sys.argv[1])
