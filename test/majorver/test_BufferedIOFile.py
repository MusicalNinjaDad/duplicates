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

def test_equal_relativepathsgiven():
    path = Path('test/data')
    file = BufferedIOFile(path)
    assert file == path
    assert file == 'test/data'

@mark.copyfiles(('fileA',1))
def test_equal_pathsresolved(copiedtestfiles):
    fileA = copiedtestfiles.paths['fileA'][0]
    symlink = copiedtestfiles.root / Path('linktoA.txt')
    try:
        symlink.symlink_to(fileA)
    except OSError as e:
        if e.winerror == 1314: skip(reason='SymLinks not available on Windows without DevMode enabled')
    assert fileA != symlink, 'Something when wrong in the test setup'
    assert fileA == symlink.resolve(), 'Something when wrong in the test setup'
    fileA = BufferedIOFile(fileA)
    assert fileA == symlink

@mark.copyfiles(('fileA',1))
def test_symlink_raiseserror(copiedtestfiles):
    fileA = copiedtestfiles.paths['fileA'][0]
    symlink = copiedtestfiles.root / Path('linktoA.txt')
    try:
        symlink.symlink_to(fileA)
    except OSError as e:
        if e.winerror == 1314: skip(reason='SymLinks not available on Windows without DevMode enabled')
    with raises(IsASymlinkError):
        symlink = BufferedIOFile(symlink)

@mark.copyfiles(('fileA',1))
def test_followsymlinks_notimplemented(copiedtestfiles):
    fileA = copiedtestfiles.paths['fileA'][0]
    symlink = copiedtestfiles.root / Path('linktoA.txt')
    try:
        symlink.symlink_to(fileA)
    except OSError as e:
        if e.winerror == 1314: skip(reason='SymLinks not available on Windows without DevMode enabled')
    with raises(NotImplementedError):
        symlink = BufferedIOFile(symlink, follow_symlinks=True)


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

def test_readchunk_zerolengthfile(tmp_path):
    zerolengthfilepath = tmp_path / Path("file00")    
    with open(zerolengthfilepath, 'w'): pass

    testfile = BufferedIOFile(zerolengthfilepath)
    with testfile.open():
        chunk = testfile.readchunk()
    assert chunk == b''

@mark.copyfiles(('fileB',1))
def test_statcache(copiedtestfiles):
    testfilepath = copiedtestfiles.paths['fileB'][0]
    testfile = BufferedIOFile(testfilepath)
    assert testfile.stat == testfilepath.stat(), f'stat is not correct.\nExpected {testfilepath.stat()}\nGot: {testfile.stat}'
    with open(testfilepath, 'w+') as file:
        file.write('stuff')
    assert testfile.stat != testfilepath.stat(), f'stat appears to have been updated or obtained realtime, not cached'
    testfile.refreshstat()
    assert testfile.stat == testfilepath.stat(), f'stat is not correct.\nExpected {testfilepath.stat()}\nGot: {testfile.stat}'