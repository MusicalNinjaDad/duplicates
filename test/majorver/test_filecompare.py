from . import listfiles, filesofsamesize, BufferedIOFile, comparefiles
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