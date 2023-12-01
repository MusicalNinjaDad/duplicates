from . import *

@mark.copyfiles(('fileA',2))
def test_replacecopywithlink(copiedtestfiles):
    assert copiedtestfiles.paths['fileA'][0].stat().st_ino != copiedtestfiles.paths['fileA'][1].stat().st_ino
    replacewithlink(copiedtestfiles.paths['fileA'][0], copiedtestfiles.paths['fileA'][1])
    assert copiedtestfiles.paths['fileA'][0].stat().st_ino == copiedtestfiles.paths['fileA'][1].stat().st_ino

@mark.copyfiles(('fileA',2),('fileB',3))
def test_findandreplacecopywithlinks(copiedtestfiles):
    linkdupes(copiedtestfiles.root)
    fileAino = copiedtestfiles.paths['fileA'][0].stat().st_ino
    fileBino = copiedtestfiles.paths['fileB'][0].stat().st_ino
    assert all(
        file.stat().st_ino == fileAino for file in copiedtestfiles.paths['fileA']
    )
    assert all(
        file.stat().st_ino == fileBino for file in copiedtestfiles.paths['fileB']
    )