from . import listfiles, filesofsamesize, BufferedIOFile, comparefiles
from .testimports import *

def test_fileissamesize(copiedtestfiles, duplicatedir1):
    filesdict = listfiles(copiedtestfiles.root)
    duplicatefiles = filesofsamesize(filesdict)
    assert duplicatefiles == {frozenset((copiedtestfiles.paths['fileA'], copiedtestfiles.paths['fileA-copy']))}

@mark.xfail
def test_samefilecontents(duplicatedir1):
    filestocompare = {frozenset(map(BufferedIOFile,(duplicatedir1.paths['fileA'], duplicatedir1.paths['fileA-copy'])))}
    identicalfiles = comparefiles(filestocompare)
    assert identicalfiles == filestocompare