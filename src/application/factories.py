import os
from base import sde
import config


def sdeManagerFromConfig():
    return sde.SDEManager(
        sdeUrl = config.SDE_URL,
        dataDir = config.SDE_DIR,
        archiveName = config.SDE_ARCHIVE_NAME,
    )
