from application.factories import sdeManagerFromConfig

def run():
    sdeClient = sdeManagerFromConfig()

    print('Removendo conteúdo SDE ...')
    sdeClient.clean()
    print('Conteúdo removido.')

