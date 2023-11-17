from collections import namedtuple
import psutil
from pytest import fixture, mark, raises
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

def test_uniquenessbasedonpath(fileA, fileB):
    testfileA = BufferedIOFile(fileA.path, fileA.handle)
    testfileB = BufferedIOFile(fileB.path, fileB.handle)
    with fileA.path.open() as fileA2Handle:
        testfileA2 = BufferedIOFile(fileA.path, fileA2Handle)
    assert testfileA == testfileA2
    assert testfileA == fileA.path
    files = {testfileA, testfileB, testfileA2}
    assert len(files) == 2
    assert files == {testfileA, testfileB} == {testfileA2, testfileB}

def test_readbychunk(fileA):
    testfile = BufferedIOFile(fileA.path, fileA.handle, chunksize=4)
    contents = [chunk for chunk in testfile]
    assert contents == [b'some', b' ran', b'dom ', b'text']

def test_notdivisiblebychunksize(fileB):
    testfile = BufferedIOFile(fileB.path, fileB.handle, chunksize=16)
    contents = [chunk for chunk in testfile]
    assert contents == [b'some longer rand', b'om text']

def test_defaultchunksize(fileA):
    testfile = BufferedIOFile(fileA.path, fileA.handle)
    contents = [chunk for chunk in testfile]
    assert contents == [b'some random text']

@mark.skip(reason="Deprecated")
def test_openhandleoninit(testfiles):
    fileApath = Path(testfiles / 'dir1' / 'fileA.txt')
    testfile = BufferedIOFile(fileApath)
    contents = [chunk for chunk in testfile]
    assert contents == [b'some random text'] # file is opened and read correctly
    thisprocess = psutil.Process()
    openfiles = thisprocess.open_files()
    assert not any(Path(f.path) == Path(fileApath) for f in openfiles) #file is closed correctly

def test_readchunk(fileB):
    testfile = BufferedIOFile(fileB.path, fileB.handle, chunksize=16)
    chunk = testfile.readchunk()
    assert chunk == b'some longer rand'
    chunk = testfile.readchunk()
    assert chunk == b'om text'