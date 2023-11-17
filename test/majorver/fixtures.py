from collections import namedtuple
from pytest import fixture
from . import dir1, dir2, Path

def openfileandreturntuple(filepath):
    with filepath.open('rb') as filehandle:
        yield(namedtuple('testfile', ['path', 'handle'])(filepath, filehandle))

@fixture
def testfiles(tmp_path) -> Path:
    dir1.copy(tmp_path)
    dir2.copy(tmp_path)
    return tmp_path

@fixture
def duplicatedir1(testfiles) -> Path:
    tmp_path = testfiles
    dir1.copy(testfiles / 'alt')
    return tmp_path

@fixture
def fileA(testfiles):
    yield from openfileandreturntuple(Path(testfiles / 'dir1' / 'fileA.txt'))

@fixture
def fileB(testfiles):
    yield from openfileandreturntuple(Path(testfiles / 'dir2' / 'fileB.txt'))