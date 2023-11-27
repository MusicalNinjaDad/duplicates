from . import listfiles, filesofsamesize, BufferedIOFile, comparefiles, drophardlinks
from .testimports import *

@mark.copyfiles(('fileA',2))
def test_fileissamesize(copiedtestfiles):
    filesdict = listfiles(copiedtestfiles.root)
    duplicatefiles = filesofsamesize(filesdict)
    assert duplicatefiles == {frozenset((copiedtestfiles.paths['fileA'][0], copiedtestfiles.paths['fileA'][1]))}

@mark.copyfiles(('fileA',2))
def test_samefilecontentsfirstchunk(copiedtestfiles, filesopen):
    filestocompare = frozenset(
        BufferedIOFile(path_handle[0], path_handle[1], chunksize=4) for path_handle in zip(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    )
    identicalfiles = comparefiles(filestocompare)
    assert identicalfiles == {filestocompare}

@mark.copyfiles(('fileA',2))
def test_samefilecontentsstopsatEOF(copiedtestfiles, filesopen):
    filestocompare = frozenset(
        BufferedIOFile(path_handle[0], path_handle[1], chunksize=4) for path_handle in zip(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    )
    chunkcount = 0
    while True:
        try:
            identicalfiles = comparefiles(filestocompare)
        except EOFError:
            break
        else:
            chunkcount += 1
    assert identicalfiles == {filestocompare}
    assert chunkcount == 4

@mark.copyfiles(('fileA',2))
@mark.linkfiles(('fileA',1))
def test_drophardlinks(copiedtestfiles, filesopen):
    filestocompare = frozenset(
        BufferedIOFile(path_handle[0], path_handle[1], chunksize=4) for path_handle in zip(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    )
    assert len(filestocompare) == 3
    identicalfiles = drophardlinks(filestocompare)
    assert len(identicalfiles) == 2
    assert BufferedIOFile(copiedtestfiles.paths['fileA'][1], copiedtestfiles.handles['fileA'][1], chunksize=4) in identicalfiles
    assert any((
        BufferedIOFile(copiedtestfiles.paths['fileA'][0], copiedtestfiles.handles['fileA'][0], chunksize=4) in identicalfiles,
        BufferedIOFile(copiedtestfiles.paths['fileA'][2], copiedtestfiles.handles['fileA'][2], chunksize=4) in identicalfiles
    ))