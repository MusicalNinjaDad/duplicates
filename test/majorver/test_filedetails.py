from recurtools import flatten

from . import listfiles
from .fixtures import *

def test_fileslisted(copiedtestfiles):
    filesdict = listfiles(copiedtestfiles.root)
    files = [file for file in flatten(filesdict.values())]
    assert len(files) == 2
    assert copiedtestfiles.paths['fileA'] in files
    assert copiedtestfiles.paths['fileB'] in files

def test_filesindexedbysize(copiedtestfiles):
    filesdict = listfiles(copiedtestfiles.root)
    assert filesdict == {
        16: copiedtestfiles.paths['fileA'],
        23: copiedtestfiles.paths['fileB']
    }

def test_filesofsamesize(duplicatedir1, fileA, fileB):
    testfiles = duplicatedir1
    filesdict = listfiles(testfiles)
    assert len(filesdict) == 2
    assert (filesdict[16]) == {
        fileA.path,
        Path(testfiles / 'alt' / 'dir1' / 'fileA.txt')
    }
    assert filesdict[23] == {fileB.path}