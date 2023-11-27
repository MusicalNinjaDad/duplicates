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

def test_samefilecontentsstopsatEOF(copiedtestfiles, duplicatedir1, fileAopened, fileAcopyopened):
    filestocompare = frozenset((
        BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'], chunksize=4),
        BufferedIOFile(copiedtestfiles.paths['fileA-copy'], copiedtestfiles.handles['fileA-copy'], chunksize=4)
    ))
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

def test_drophardlinks(copiedtestfiles, duplicatedir1, fileAopened, fileAcopyopened, fileAhardlinked, fileAlinkopened):
    filestocompare = frozenset((
        BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'], chunksize=4),
        BufferedIOFile(copiedtestfiles.paths['fileA-copy'], copiedtestfiles.handles['fileA-copy'], chunksize=4),
        BufferedIOFile(copiedtestfiles.paths['fileA-link'], copiedtestfiles.handles['fileA-link'], chunksize=4),
    ))
    identicalfiles = drophardlinks(filestocompare)
    assert len(identicalfiles) == 2
    assert BufferedIOFile(copiedtestfiles.paths['fileA-copy'], copiedtestfiles.handles['fileA-copy'], chunksize=4) in identicalfiles
    assert any((
        BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'], chunksize=4) in identicalfiles,
        BufferedIOFile(copiedtestfiles.paths['fileA-link'], copiedtestfiles.handles['fileA-link'], chunksize=4) in identicalfiles
    ))