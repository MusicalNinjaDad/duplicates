from recurtools import flatten

from . import listfiles, Path
from .fixtures import *

def test_fileslisted(testfiles, fileA, fileB):
    filesdict = listfiles(testfiles)
    files = [file for file in flatten(filesdict.values())]
    assert len(files) == 2
    assert fileA.path in files
    assert fileB.path in files

def test_filesindexedbysize(testfiles, fileA, fileB):
    filesdict = listfiles(testfiles)
    assert filesdict == {
        16: {fileA.path},
        23: {fileB.path}
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