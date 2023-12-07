from pathlib import Path

from . import *

@mark.copyfiles(('fileA',1))
def test_initialisation(copiedtestfiles, filesopen):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileA'][0], copiedtestfiles.handles['fileA'][0])
    assert testfile.path == copiedtestfiles.paths['fileA'][0]
    assert testfile.handle == copiedtestfiles.handles['fileA'][0]

@mark.copyfiles(('fileA',1), ('fileB', 1))
def test_immutability(copiedtestfiles, filesopen):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileA'][0], copiedtestfiles.handles['fileA'][0])
    with raises(AttributeError):
        testfile.path = Path('dir1')
    with raises(AttributeError):
        testfile.handle = copiedtestfiles.handles['fileB'][0]

@mark.copyfiles(('fileA',1), ('fileB', 1))
def test_hashable(copiedtestfiles, filesopen):
    testfileA = BufferedIOFile(copiedtestfiles.paths['fileA'][0], copiedtestfiles.handles['fileA'][0])
    testfileB = BufferedIOFile(copiedtestfiles.paths['fileB'][0], copiedtestfiles.handles['fileB'][0])
    files = {testfileA, testfileB}
    assert files

@mark.copyfiles(('fileA',1), ('fileB', 1))
def test_uniquenessbasedonpath(copiedtestfiles, filesopen):
    testfileA = BufferedIOFile(copiedtestfiles.paths['fileA'][0], copiedtestfiles.handles['fileA'][0])
    testfileB = BufferedIOFile(copiedtestfiles.paths['fileB'][0], copiedtestfiles.handles['fileB'][0])
    with copiedtestfiles.paths['fileA'][0].open() as fileA2Handle:
        testfileA2 = BufferedIOFile(copiedtestfiles.paths['fileA'][0], fileA2Handle)
    assert testfileA == testfileA2
    assert testfileA == copiedtestfiles.paths['fileA'][0]
    files = {testfileA, testfileB, testfileA2}
    assert len(files) == 2
    assert files == {testfileA, testfileB} == {testfileA2, testfileB}

@mark.copyfiles(('fileA',1))
def test_readbychunk(copiedtestfiles, filesopen):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileA'][0], copiedtestfiles.handles['fileA'][0], chunksize=4)
    contents = [chunk for chunk in testfile]
    assert contents == [b'some', b' ran', b'dom ', b'text']

@mark.copyfiles(('fileB',1))
def test_notdivisiblebychunksize(copiedtestfiles, filesopen):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileB'][0], copiedtestfiles.handles['fileB'][0], chunksize=16)
    contents = [chunk for chunk in testfile]
    assert contents == [b'some longer rand', b'om text']

@mark.copyfiles(('fileA',1))
def test_defaultchunksize(copiedtestfiles, filesopen):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileA'][0], copiedtestfiles.handles['fileA'][0])
    contents = [chunk for chunk in testfile]
    assert contents == [b'some random text']

@mark.copyfiles(('fileB',1))
def test_readchunk(copiedtestfiles, filesopen):
    testfile = BufferedIOFile(copiedtestfiles.paths['fileB'][0], copiedtestfiles.handles['fileB'][0], chunksize=16)
    chunk = testfile.readchunk()
    assert chunk == b'some longer rand'
    chunk = testfile.readchunk()
    assert chunk == b'om text'

@mark.copyfiles(('fileA',1))
def test_open(copiedtestfiles):
        testfile = BufferedIOFile(copiedtestfiles.paths['fileA'][0], chunksize=4)
        assert not testfile.handle
        with testfile.open():
            assert testfile.handle
            assert testfile.readchunk() == b'some'
        assert not testfile.handle
        with raises(ValueError):
            testfile.readchunk()