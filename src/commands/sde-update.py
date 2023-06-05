from application.factories import sdeManagerFromConfig
from base.sde import SDEFetchLinkNotFoundException


def getSDEDownloadLink(sdeManager):
    url = None
    try:
        url = sdeManager.resolveSDELink()
    except SDEFetchLinkNotFoundException as e:
        print('Não foi possível obter o link do SDE a partir da homepage')
        exit(1)

    return url


def run():
    sde = sdeManagerFromConfig()

    print('Obtendo endereço para download ...')
    url = getSDEDownloadLink(sde)

    print('Baixando novo arquivo SDE ...')
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
