import os
from . import listfiles, filesofsamesize, BufferedIOFile, comparefiles, drophardlinks
from .testimports import *

def test_fileissamesize(copiedtestfiles, duplicatedir1):
    filesdict = listfiles(copiedtestfiles.root)
    duplicatefiles = filesofsamesize(filesdict)
    assert duplicatefiles == {frozenset((copiedtestfiles.paths['fileA'], copiedtestfiles.paths['fileA-copy']))}

def test_samefilecontentsfirstchunk(copiedtestfiles, duplicatedir1, fileAopened, fileAcopyopened):
    filestocompare = frozenset((
        BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'], chunksize=4),
        BufferedIOFile(copiedtestfiles.paths['fileA-copy'], copiedtestfiles.handles['fileA-copy'], chunksize=4)
    ))
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
    assert identicalfiles == frozenset((
        BufferedIOFile(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'], chunksize=4),
        BufferedIOFile(copiedtestfiles.paths['fileA-copy'], copiedtestfiles.handles['fileA-copy'], chunksize=4)
    ))