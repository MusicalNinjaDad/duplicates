from recurtools import flatten

from . import listfiles
from .testimports import *

@mark.copyfiles(('fileA',1), ('fileB',1))
def test_fileslisted(copiedtestfiles):
    filesdict = listfiles(copiedtestfiles.root)
    files = [file for file in flatten(filesdict.values())]
    assert len(files) == 2
    assert copiedtestfiles.paths['fileA'][0] in files
    assert copiedtestfiles.paths['fileB'][0] in files

@mark.copyfiles(('fileA',1), ('fileB',1))
def test_filesindexedbysize(copiedtestfiles):
    filesdict = listfiles(copiedtestfiles.root)
    assert filesdict == {
        16: {copiedtestfiles.paths['fileA'][0]},
        23: {copiedtestfiles.paths['fileB'][0]}
    }

@mark.copyfiles(('fileA', 2), ('fileB',1))
def test_filesofsamesize(copiedtestfiles):
    filesdict = listfiles(copiedtestfiles.root)
    assert len(filesdict) == 2
    assert filesdict[16] == {
        copiedtestfiles.paths['fileA'][0],
        copiedtestfiles.paths['fileA'][1]
    }
    assert filesdict[23] == {copiedtestfiles.paths['fileB'][0]}