from contextlib import contextmanager
import os

@contextmanager
def pushd(targetDir):
    currentDir = os.getcwd()
    os.chdir(targetDir)
    yield os.getcwd()
    os.chdir(currentDir)