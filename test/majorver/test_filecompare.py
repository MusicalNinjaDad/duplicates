from . import listfiles, filesofsamesize, BufferedIOFile, comparefiles
from .fixtures import *

def test_fileissamesize(duplicatedir1):
    filesdict = listfiles(duplicatedir1.root)
    duplicatefiles = filesofsamesize(filesdict)
    assert duplicatefiles == {frozenset((duplicatedir1.paths['fileA'], duplicatedir1.paths['fileA-copy']))}

@mark.xfail
def test_samefilecontents(duplicatedir1):
    filestocompare = {frozenset(map(BufferedIOFile,(duplicatedir1.paths['fileA'], duplicatedir1.paths['fileA-copy'])))}
    identicalfiles = comparefiles(filestocompare)
    assert identicalfiles == filestocompare