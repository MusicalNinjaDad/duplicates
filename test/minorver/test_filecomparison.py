from . import *
from ...duplicates.dupes import _comparefilechunk, _indexbyino, _filesofsamesize

@mark.copyfiles(('fileA',2))
def test_fileissamesize(copiedtestfiles):
    duplicatefiles = _filesofsamesize((copiedtestfiles.root,))
    assert duplicatefiles == {frozenset((copiedtestfiles.paths['fileA'][0], copiedtestfiles.paths['fileA'][1]))}

@mark.copyfiles(('fileA',2))
def test_zerosizefile(copiedtestfiles):
    with open(copiedtestfiles.root / Path("file0"), 'w'): pass
    duplicatefiles = _filesofsamesize((copiedtestfiles.root,))
    assert duplicatefiles == {frozenset((copiedtestfiles.paths['fileA'][0], copiedtestfiles.paths['fileA'][1]))}

@mark.copyfiles(('fileA',2))
def test_samefilecontentsfirstchunk(copiedtestfiles, filesopen):
    filestocompare = frozenset(
        BufferedIOFile(path_handle[0], handle=path_handle[1], chunksize=4) for path_handle in zip(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    )
    identicalfiles = _comparefilechunk(filestocompare)
    assert identicalfiles == {filestocompare}

@mark.copyfiles(('fileA',2))
def test_samefilecontentsstopsatEOF(copiedtestfiles, filesopen):
    filestocompare = frozenset(
        BufferedIOFile(path_handle[0], handle=path_handle[1], chunksize=4) for path_handle in zip(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    )
    chunkcount = 0
    while True:
        try:
            identicalfiles = _comparefilechunk(filestocompare)
        except EOFError:
            break
        else:
            chunkcount += 1
    assert identicalfiles == {filestocompare}
    assert chunkcount == 4

@mark.copyfiles(('fileA',2))
@mark.linkfiles(('fileA',1))
def test_indexbyino(copiedtestfiles):
    filestocompare = frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileA'])
    assert len(filestocompare) == 3
    inoindex = _indexbyino(filestocompare)
    assert len(inoindex) == 2
    assert {copiedtestfiles.paths['fileA'][0], copiedtestfiles.paths['fileA'][2]} in inoindex.values()
    assert {copiedtestfiles.paths['fileA'][1]} in inoindex.values()

@mark.copyfiles(('fileA',1))
@mark.linkfiles(('fileA',2))
def test_dontscanoridentifyifonlylinks(copiedtestfiles, monkeypatch):
    """This can waste a lot of time if there are files which have already been processed by a previous run of dupes and no new copies are present.
    """
    class InvalidCallToOpenError(Exception):
            pass
    
    @contextmanager
    def _dontopen(self):
        raise InvalidCallToOpenError
    
    from ...duplicates.bufferediofile import BufferedIOFile
    monkeypatch.setattr(BufferedIOFile, 'open', _dontopen)
    
    # Validating monkeypatch worked
    t = BufferedIOFile(copiedtestfiles.paths['fileA'][0])
    with raises(InvalidCallToOpenError), t.open():
        assert True

    duplicatefiles = DuplicateFiles.frompaths(copiedtestfiles.root)
    assert not duplicatefiles.duplicates