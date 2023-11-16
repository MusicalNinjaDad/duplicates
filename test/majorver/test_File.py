from collections import namedtuple
from pytest import fixture, raises
from pathlib import Path

from . import BufferedIOFile, testfiles

@fixture
def fileA(testfiles):
    yield from openfileandreturntuple(Path(testfiles / 'dir1' / 'fileA.txt'))

@fixture
def fileB(testfiles):
    yield from openfileandreturntuple(Path(testfiles / 'dir2' / 'fileB.txt'))

def openfileandreturntuple(filepath):
    with filepath.open('rb') as filehandle:
        yield(namedtuple('testfile', ['path', 'handle'])(filepath, filehandle))


def test_initialisation(fileA):
    testfile = BufferedIOFile(fileA.path, fileA.handle)
    assert testfile.path == fileA.path
    assert testfile.handle == fileA.handle

def test_immutability(fileA, fileB):
    testfile = BufferedIOFile(fileA.path, fileA.handle)
    with raises(AttributeError):
        testfile.path = Path('dir1')
    with raises(AttributeError):
        testfile.handle = fileB.handle

def test_hashable(fileA, fileB):
        testfileA = BufferedIOFile(fileA.path, fileA.handle)
        testfileB = BufferedIOFile(fileB.path, fileB.handle)
        files = {testfileA, testfileB}
        assert files