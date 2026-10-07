import os
from base import sde
from base.evecli import cli


def sdeManagerFromConfig():
    return sde.SDEManager(
        sdeUrl = cli.SDE_URL,
        dataDir = cli.SDE_DIR,
        archiveName = cli.SDE_ARCHIVE_NAME,
    )
