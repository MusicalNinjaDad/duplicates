from . import BufferedIOFile
from .testimports import *

def test_initialisation(copiedtestfiles, fileAopened):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    assert testfile.path == copiedtestfiles.paths['fileA']
    assert testfile.handle == copiedtestfiles.handles['fileA']

def test_immutability(copiedtestfiles, fileAopened, fileBopened):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    with raises(AttributeError):
        testfile.path = Path('dir1')
    with raises(AttributeError):
        testfile.handle = copiedtestfiles.handles['fileB']

def test_hashable(copiedtestfiles, fileAopened, fileBopened):
    testfileA = BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    testfileB = BufferedIOFile(copiedtestfiles.paths['fileB'], copiedtestfiles.handles['fileB'])
    files = {testfileA, testfileB}
    assert files

def test_uniquenessbasedonpath(copiedtestfiles, fileAopened, fileBopened):
    testfileA = BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    testfileB = BufferedIOFile(copiedtestfiles.paths['fileB'], copiedtestfiles.handles['fileB'])
    with copiedtestfiles.paths['fileA'].open() as fileA2Handle:
        testfileA2 = BufferedIOFile(copiedtestfiles.paths['fileA'], fileA2Handle)
    assert testfileA == testfileA2
    assert testfileA == copiedtestfiles.paths['fileA']
    files = {testfileA, testfileB, testfileA2}
    assert len(files) == 2
    assert files == {testfileA, testfileB} == {testfileA2, testfileB}

def test_readbychunk(copiedtestfiles, fileAopened):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'], chunksize=4)
    contents = [chunk for chunk in testfile]
    assert contents == [b'some', b' ran', b'dom ', b'text']

def test_notdivisiblebychunksize(copiedtestfiles, fileBopened):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileB'], copiedtestfiles.handles['fileB'], chunksize=16)
    contents = [chunk for chunk in testfile]
    assert contents == [b'some longer rand', b'om text']

def test_defaultchunksize(copiedtestfiles, fileAopened):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    contents = [chunk for chunk in testfile]
    assert contents == [b'some random text']

def test_readchunk(copiedtestfiles, fileBopened):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileB'], copiedtestfiles.handles['fileB'], chunksize=16)
    chunk = testfile.readchunk()
    assert chunk == b'some longer rand'
    chunk = testfile.readchunk()
    assert chunk == b'om text'