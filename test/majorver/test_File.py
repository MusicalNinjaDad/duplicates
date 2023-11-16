from collections import namedtuple
from pytest import fixture
from pathlib import Path

from . import BufferedIOFile, testfiles

@fixture
def fileA(testfiles):
    testfilepath = Path(testfiles / 'dir1' / 'fileA.txt')
    with testfilepath.open('rb') as testfilehandle:
        yield(namedtuple('testfile', ['path', 'handle'])(testfilepath, testfilehandle))

def test_initialisation(fileA):
    testfile = BufferedIOFile(fileA.path, fileA.handle)
    assert testfile.path == fileA.path
    assert testfile.handle == fileA.handle