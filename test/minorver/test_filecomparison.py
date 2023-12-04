from . import *
from ...duplicates.dupes import _comparefilechunk, _drophardlinks, _filesofsamesize

@mark.copyfiles(('fileA',2))
def test_fileissamesize(copiedtestfiles):
    duplicatefiles = _filesofsamesize(copiedtestfiles.root)
    assert duplicatefiles == {frozenset((copiedtestfiles.paths['fileA'][0], copiedtestfiles.paths['fileA'][1]))}

@mark.copyfiles(('fileA',2))
def test_samefilecontentsfirstchunk(copiedtestfiles, filesopen):
    filestocompare = frozenset(
        BufferedIOFile(path_handle[0], path_handle[1], chunksize=4) for path_handle in zip(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    )
    identicalfiles = _comparefilechunk(filestocompare)
    assert identicalfiles == {filestocompare}

@mark.copyfiles(('fileA',2))
def test_samefilecontentsstopsatEOF(copiedtestfiles, filesopen):
    filestocompare = frozenset(
        BufferedIOFile(path_handle[0], path_handle[1], chunksize=4) for path_handle in zip(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
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
def test_drophardlinks(copiedtestfiles):
    filestocompare = frozenset(path for path in copiedtestfiles.paths['fileA'])
    assert len(filestocompare) == 3
    identicalfiles = _drophardlinks(filestocompare)
    assert len(identicalfiles) == 2
    assert copiedtestfiles.paths['fileA'][1] in identicalfiles
    assert any((
        copiedtestfiles.paths['fileA'][0] in identicalfiles,
        copiedtestfiles.paths['fileA'][2] in identicalfiles
    ))