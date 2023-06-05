import re
import os
import sys
import shutil
import zipfile
import requests
import yaml

from lxml import etree

from utils import *
from support.filesystem import pushd


class SDEException(Exception):
    pass


class SDEFetchLinkNotFoundException(SDEException):
    def __init__(self, message = None):
        message = 'Unable to find link to fetch SDE data'
        super().__init__(message)


class SDEManager:
    BLUEPRINT_FILE_PATH = os.path.normpath('sde/fsd/blueprints.yaml')
    TYPEID_INDEX_FILE_PATH = os.path.normpath('resources/typeIDs.idx')
    BLUEPRINT_TYPEID_INDEX_FILE_PATH = os.path.normpath('resources/blueprintTypeIDs.idx')
    TYPE_ID_FILE_PATH = os.path.normpath('sde/fsd/typeIDs.yaml')


    def __init__(self, sdePageUrl, sdeLinkText, dataDir, archiveName):
        self.sdePageUrl = sdePageUrl
        self.sdeLinkText = sdeLinkText
        self.dataDir = os.path.abspath(os.path.normpath(dataDir))
        self.archiveName = archiveName
        self.typeIdIndex = None
        self.blueprintTypeIdIndex = None


    @property
    def sdeFilePath(self):
        return os.path.join(self.dataDir, self.archiveName)

    @property
    def blueprintsDir(self):
        return os.path.join(self.dataDir, 'blueprints')

    def blueprintPath(self, blueprintId):
        return os.path.join(self.blueprintsDir, f'{blueprintId}.json')

    @property
    def blueprintFilePath(self):
        return os.path.join(self.dataDir, self.BLUEPRINT_FILE_PATH)

    def resolveSDELink(self):
        sdePage = requests.get(self.sdePageUrl)
        root = etree.HTML(sdePage.text)

        linkElements = root.xpath(f'//a[text()="{self.sdeLinkText}"]')
        if linkElements == []:
            return None

        linkElement = linkElements[0]
        sdeUrl = linkElement.get('href')
        if sdeUrl is None:
            raise SDEFetchLinkNotFoundException()

        return sdeUrl


    def fetchSDEArchive(self, url):
        response = requests.get(url)
        ensureDir(self.dataDir)
        with open(self.sdeFilePath, 'wb') as sdeFile:
            sdeFile.write(response.content)


    def extract(self):
        with zipfile.ZipFile(self.sdeFilePath) as sdeArchive:
            sdeArchive.extractall(self.dataDir)


    def clean(self):
        shutil.rmtree(self.dataDir)
        ensureDir(self.dataDir)


    def expandBlueprints(self):
        # Reading blueprints file from SDE
        blueprints = None
        with open(self.blueprintFilePath) as inputDataFile:
            blueprints = yaml.safe_load(inputDataFile)

        # Saving individual blueprint files
        if blueprints is not None:
            ensureDir(self.blueprintsDir)
            for blueprintId, blueprintData in blueprints.items():
                bpFileName = f'{blueprintId}.json'
                print(f'  Saving: {bpFileName}')
                with open(os.path.join(self.blueprintsDir, bpFileName), 'w') as jsonOutput:
                    content = json.dumps(blueprintData)
                    jsonOutput.write(content)


    def buildTypeIdIndex(self):
        typeIdMap = self.buildTypeIdMap()
        with open(self.TYPEID_INDEX_FILE_PATH, 'w', encoding='utf-8') as indexFile:
            for name, id in typeIdMap.items():
                indexFile.write(f'{name}\t{id}\n')


    def buildTypeIdMap(self):
        items = None
        with open(os.path.join(self.dataDir, self.TYPE_ID_FILE_PATH), encoding='utf-8') as inputDataFile:
            items = yaml.safe_load(inputDataFile)

        mapping = {}
        for typeId, item in items.items():
            if item.get('name', {}).get('en') == None:
                print(f'!!! Item Name Not Found: {typeId}')
                continue
            mapping[item['name']['en']] = typeId

        return mapping


    def buildBlueprintTypeIdIndex(self):
        return self.createIndexFile(self.BLUEPRINT_TYPEID_INDEX_FILE_PATH, self.buildBlueprintTypeIdMap())


    def createIndexFile(self, filepath, data):
        with open(filepath, 'w', encoding='utf-8') as indexFile:
            for name, id in data.items():
                indexFile.write(f'{name}\t{id}\n')


    def buildBlueprintTypeIdMap(self):
        bpMap = {}
        bpIds = self.blueprintIds
        for bpId in bpIds:
            blueprint = self.loadBlueprintById(bpId)
            try:
                for product in blueprint['activities']['manufacturing']['products']:
                    itemId = product['typeID']
                    bpMap[itemId] = bpId
            except Exception as e:
                print(f'Error processing bpId #{bpId}: ', e.__class__.__name__, e)
        return bpMap


    def loadTypeIDIndex(self):
        if self.typeIdIndex is None:
            self.typeIdIndex = self.loadIndex(self.TYPEID_INDEX_FILE_PATH)


    def loadBlueprintTypeIDIndex(self):
        if self.blueprintTypeIdIndex is None:
            self.blueprintTypeIdIndex = self.loadIndex(self.BLUEPRINT_TYPEID_INDEX_FILE_PATH)


    def loadIndex(self, indexFilePath):
        index = {}
        with open(indexFilePath, encoding='utf-8') as inputFile:
            for line in inputFile.readlines():
                if line.strip() == '':
                    continue
                name, typeId = line.strip().split('\t')
                index[name] = typeId
        return index


    def searchItem(self, term):
        self.loadTypeIDIndex()

        pattern = re.compile(term, re.IGNORECASE)
        results = []
        for name, typeId in self.typeIdIndex.items():
            m = pattern.search(name)
            if m is not None:
                results.append({
                    'type_id': typeId,
                    'name': name,
                })
        return results


    def loadBlueprint(self, blueprintPath):
        blueprint = None
        with open(blueprintPath) as bpFile:
            blueprint = json.load(bpFile)
        return blueprint


    def loadBlueprintById(self, blueprintId):
        blueprint = None

        try:
            blueprint = self.loadBlueprint(self.blueprintPath(blueprintId))
            #with open(self.blueprintPath(blueprintId)) as bpFile:
            #    blueprint = json.load(bpFile)
        except FileNotFoundError:
            raise Exception(f'Could not find blueprint: {blueprintId}')

        return blueprint


    @property
    def blueprintIds(self):
        ids = []
        with pushd(self.blueprintsDir):
            ids = map(lambda n: n.rstrip('.json'), filter(lambda fname: fname.endswith('.json'), os.listdir('.')))
            ids = list(map(int, ids))
        return ids


    def getItemBlueprint(self, itemId):
        self.loadBlueprintTypeIDIndex()
        bpId = self.blueprintTypeIdIndex.get(itemId)
        if bpId is None:
            return None

        return self.loadBlueprintById(bpId)
