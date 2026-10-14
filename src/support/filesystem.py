from contextlib import contextmanager
import os
from pathlib import Path


@contextmanager
def pushd(targetDir):
    currentDir = os.getcwd()
    os.chdir(targetDir)
    yield os.getcwd()
    os.chdir(currentDir)


def touch(path):
    Path(path).touch()


def ensureDir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok = True)