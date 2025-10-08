from application.factories import sdeManagerFromConfig
from base.sde import SDEFetchLinkNotFoundException


def run():
    sde = sdeManagerFromConfig()

    print('Obtendo endereço para download ...')
    url = sde.sdeUrl

    print(f'Baixando novo arquivo SDE de "{url}" ...')
    sde.fetchSDEArchive(url)
    print('Arquivo SDE baixado com sucesso.')

    print('Extraindo conteúdo do arquivo SDE compactado ...')
    sde.extract()
    print('Arquivo extraido com sucesso.')

    print('Expandindo blueprints ...')
    sde.expandBlueprints()

    print('Expandindo type ids ...')
    sde.buildTypeIdIndex()
    sde.buildBlueprintTypeIdIndex()
