import os
from base import sde
import config

def sdeManagerFromConfig():
    return sde.SDEManager(
        sdePageUrl = config.EVE_SDE_PAGE_URL,
        sdeLinkText = config.EVE_SDE_LINK_TEXT,
        dataDir = config.SDE_DIR,
        archiveName = config.SDE_ARCHIVE_NAME,
    )
