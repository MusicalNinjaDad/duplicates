from . import BufferedIOFile
from .testimports import *

def test_initialisation(fileAopened):
    testfile = BufferedIOFile(fileAopened.paths['fileA'], fileAopened.handles['fileA'])
    assert testfile.path == fileAopened.paths['fileA']
    assert testfile.handle == fileAopened.handles['fileA']

def test_immutability(fileAopened, fileBopened):
    testfile = BufferedIOFile(fileAopened.paths['fileA'], fileAopened.handles['fileA'])
    with raises(AttributeError):
        testfile.path = Path('dir1')
    with raises(AttributeError):
        testfile.handle = fileBopened.handles['fileB']

def test_hashable(fileAopened, fileBopened):
    testfileA = BufferedIOFile(fileAopened.paths['fileA'], fileAopened.handles['fileA'])
    testfileB = BufferedIOFile(fileBopened.paths['fileB'], fileBopened.handles['fileB'])
    files = {testfileA, testfileB}
    assert files

def test_uniquenessbasedonpath(fileAopened, fileBopened):
    testfileA = BufferedIOFile(fileAopened.paths['fileA'], fileAopened.handles['fileA'])
    testfileB = BufferedIOFile(fileBopened.paths['fileB'], fileBopened.handles['fileB'])
    with fileAopened.paths['fileA'].open() as fileA2Handle:
        testfileA2 = BufferedIOFile(fileAopened.paths['fileA'], fileA2Handle)
    assert testfileA == testfileA2
    assert testfileA == fileAopened.paths['fileA']
    files = {testfileA, testfileB, testfileA2}
    assert len(files) == 2
    assert files == {testfileA, testfileB} == {testfileA2, testfileB}

def test_readbychunk(fileAopened):
    testfile = BufferedIOFile(fileAopened.paths['fileA'], fileAopened.handles['fileA'], chunksize=4)
    contents = [chunk for chunk in testfile]
    assert contents == [b'some', b' ran', b'dom ', b'text']

def test_notdivisiblebychunksize(fileBopened):
    testfile = BufferedIOFile(fileBopened.paths['fileB'], fileBopened.handles['fileB'], chunksize=16)
    contents = [chunk for chunk in testfile]
    assert contents == [b'some longer rand', b'om text']

def test_defaultchunksize(fileAopened):
    testfile = BufferedIOFile(fileAopened.paths['fileA'], fileAopened.handles['fileA'])
    contents = [chunk for chunk in testfile]
    assert contents == [b'some random text']

def test_readchunk(fileBopened):
    testfile = BufferedIOFile(fileBopened.paths['fileB'], fileBopened.handles['fileB'], chunksize=16)
    chunk = testfile.readchunk()
    assert chunk == b'some longer rand'
    chunk = testfile.readchunk()
    assert chunk == b'om text'